from fastapi import FastAPI, Request
import httpx

app = FastAPI()
TARGET_BASE = "https://7043eb19dc52-greflix.baby-beamup.club"

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path_name: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{TARGET_BASE}/{path_name}"
        if request.url.query:
            url += f"?{request.url.query}"

        response = await client.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers.items() if k.lower() != 'host'}
        )

        try:
            data = response.json()
            if "meta" in data and "videos" in data["meta"]:
                for video in data["meta"]["videos"]:
                    if "episode" in video and isinstance(video["episode"], float):
                        video["episode"] = int(video["episode"])
            return data
        except:
            return response.content
