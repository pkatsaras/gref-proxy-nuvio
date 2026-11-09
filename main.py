from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()
TARGET_BASE = "https://7043eb19dc52-greflix.baby-beamup.club"

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path_name: str):
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        url = f"{TARGET_BASE}/{path_name}"
        if request.url.query:
            url += f"?{request.url.query}"
        
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'accept-encoding']}
        
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers
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
            return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))
