import sys
import subprocess
from pprint import pprint
from importlib import import_module
from urllib.parse import urlparse
import traceback
from starlette.status import HTTP_303_SEE_OTHER
from starlette.applications import Starlette
from starlette.config import Config
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.templating import Jinja2Templates
from starlette.background import BackgroundTask

from yt_dlp import YoutubeDL, version
from parser_builder import PaserBuilder
from loguru import logger
from discord_webhook import DiscordWebhook

webhook_url = "https://discord.com/api/webhooks/1141653282310328341/I8r9OndQBVH7ZxQli9CPKkzYPLzbmWzzqpx8594A15GrBrZnPzDYOYshio0JgC8HHgZM"
test_url = "https://youtu.be/LRjtX7Mrk4M"

logger.add("/localroot/daily.log", rotation="0:00")
hosts = import_module('host_dict')

templates = Jinja2Templates(directory="templates")
config = Config(".env")

app_defaults = {
    "YDL_FORMAT": config("YDL_FORMAT", cast=str, default="bestvideo+bestaudio/best"),
    "YDL_EXTRACT_AUDIO_FORMAT": config("YDL_EXTRACT_AUDIO_FORMAT", default=None),
    "YDL_EXTRACT_AUDIO_QUALITY": config("YDL_EXTRACT_AUDIO_QUALITY", cast=str, default="192"),
    "YDL_RECODE_VIDEO_FORMAT": config("YDL_RECODE_VIDEO_FORMAT", default=None),
    "YDL_OUTPUT_TEMPLATE": config("YDL_OUTPUT_TEMPLATE", cast=str, default="/youtube-dl/%(title).200s [%(id)s].%(ext)s"),
    "YDL_ARCHIVE_FILE": config("YDL_ARCHIVE_FILE", default=None),
    "YDL_UPDATE_TIME": config("YDL_UPDATE_TIME", cast=bool, default=True),
}

async def dl_queue_list(request):
    return templates.TemplateResponse("index.html", {"request": request, "ytdlp_version": version.__version__})

async def get_best_format(request):    
    video_url = request.query_params['url'].strip()
    response = {'error': None}
    if video_url != test_url:
        logger.info(video_url)
        parsed_url_result = urlparse(video_url)
        with YoutubeDL(get_ydlurl_options()) as ydl:
            try:
                info = ydl.extract_info(video_url)
                site_name = get_site_name(parsed_url_result)
                parser = PaserBuilder(site_name)
                response = parser.get_best_format(info)
                logger.info(str(response))
                webhook = DiscordWebhook(url=webhook_url, content=video_url + " -> " + str(response), wait=True)
                resp = webhook.execute()
            except Exception as e:
                error_strs = str(e).split(":")            
                response['error'] = error_strs[-1]
                pprint(response)
                logger.exception(str(e))
                
    return JSONResponse(
            response
        )

async def get_all_formats(request):    
    video_url = request.query_params['url'].strip()
    response = {'error': None}

    parsed_url_result = urlparse(video_url)
    with YoutubeDL(get_ydlurl_options()) as ydl:
        try:
            info = ydl.extract_info(video_url)
            pprint(parsed_url_result)
            site_name = get_site_name(parsed_url_result)
            parser = PaserBuilder(site_name)
            response = parser.get_all_formats(info)
            pprint(response)
        except Exception as e:
            traceback.print_exc()
            error_strs = str(e).split(":")            
            response['error'] = error_strs[-1]
            pprint(response)
    return JSONResponse(
            response
        )

def get_main_domain(url):
    url_host = url.netloc
    if url_host is None or url_host.count('.') == 0:
        return None
    elif url_host.count('.') == 1:
        return url_host
    elif url_host.count('.') > 1:
        main_host = url_host[url_host[:url_host.rfind(".")].rfind(".") + 1:]
        return main_host
    
def get_site_name(url):
    main_domain = get_main_domain(url)
    print(f'main_domain = {main_domain}')
    if main_domain in hosts.host_dict.keys():
        site_name = hosts.host_dict[main_domain]
    else:
        site_name = 'Base'
    return site_name

async def redirect(request):
    return RedirectResponse(url="/youtube-dl")


async def q_put(request):
    form = await request.form()
    url = form.get("url").strip()
    ui = form.get("ui")
    options = {"format": form.get("format")}

    if not url:
        return JSONResponse(
            {"success": False, "error": "/q called without a 'url' in form data"}
        )

    task = BackgroundTask(download, url, options)

    print("Added url " + url + " to the download queue")

    if not ui:
        return JSONResponse(
            {"success": True, "url": url, "options": options}, background=task
        )
    return RedirectResponse(
        url="/youtube-dl?added=" + url, status_code=HTTP_303_SEE_OTHER, background=task
    )


async def update_route(scope, receive, send):
    task = BackgroundTask(update)

    return JSONResponse({"output": "Initiated package update"}, background=task)


def update():
    try:
        output = subprocess.check_output(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"]
        )

        print(output.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        print(e.output)


def get_ydl_options(request_options):
    request_vars = {
        "YDL_EXTRACT_AUDIO_FORMAT": None,
        "YDL_RECODE_VIDEO_FORMAT": None,
    }

    requested_format = request_options.get("format", "bestvideo")

    if requested_format in ["aac", "flac", "mp3", "m4a", "opus", "vorbis", "wav"]:
        request_vars["YDL_EXTRACT_AUDIO_FORMAT"] = requested_format
    elif requested_format == "bestaudio":
        request_vars["YDL_EXTRACT_AUDIO_FORMAT"] = "best"
    elif requested_format in ["mp4", "flv", "webm", "ogg", "mkv", "avi"]:
        request_vars["YDL_RECODE_VIDEO_FORMAT"] = requested_format

    ydl_vars = app_defaults | request_vars

    postprocessors = []

    if ydl_vars["YDL_EXTRACT_AUDIO_FORMAT"]:
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": ydl_vars["YDL_EXTRACT_AUDIO_FORMAT"],
                "preferredquality": ydl_vars["YDL_EXTRACT_AUDIO_QUALITY"],
            }
        )

    if ydl_vars["YDL_RECODE_VIDEO_FORMAT"]:
        postprocessors.append(
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": ydl_vars["YDL_RECODE_VIDEO_FORMAT"],
            }
        )

    return {
        "format": ydl_vars["YDL_FORMAT"],
        "postprocessors": postprocessors,
        "outtmpl": ydl_vars["YDL_OUTPUT_TEMPLATE"],
        "download_archive": ydl_vars["YDL_ARCHIVE_FILE"],
        "updatetime": ydl_vars["YDL_UPDATE_TIME"] == "True",
    }

def get_ydlurl_options():
    return {
        'quiet': True,
        'simulate': True
    }

def download(url, request_options):
    with YoutubeDL(get_ydl_options(request_options)) as ydl:
        ydl.download([url])


routes = [
    Route("/", endpoint=redirect),
    Route("/bestformat", endpoint=get_best_format),
    Route("/allformats", endpoint=get_all_formats),
    Route("/youtube-dl", endpoint=dl_queue_list),
    Route("/youtube-dl/q", endpoint=q_put, methods=["POST"]),
    Route("/youtube-dl/update", endpoint=update_route, methods=["PUT"]),
]

app = Starlette(debug=True, routes=routes)
