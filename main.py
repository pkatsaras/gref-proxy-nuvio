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
        
        content = response.content
        try:
            data = response.json()
            
            # Διορθώνουμε αναδρομικά τυχόν δεκαδικά επεισόδια παντού
            def fix_episodes(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == "episode" and isinstance(v, float):
                            obj[k] = int(v)
                        else:
                            fix_episodes(v)
                elif isinstance(obj, list):
                    for item in obj:
                        fix_episodes(item)
            
            fix_episodes(data)
            return data
        except Exception:
            return {"error": False, "message": content.decode("utf-8", errors="ignore")}
