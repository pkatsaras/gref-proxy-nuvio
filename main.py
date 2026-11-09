from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()
TARGET_BASE = "https://7043eb19dc52-greflix.baby-beamup.club"

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path_name: str):
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            url = f"{TARGET_BASE}/{path_name}"
            if request.url.query:
                url += f"?{request.url.query}"
            
            # Καθαρίζουμε τα headers ζήτησης
            headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'accept-encoding', 'connection']}
            
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers
            )
            
            # Προσπάθεια 1: Αν είναι καθαρό JSON, το διορθώνουμε αναδρομικά
            try:
                data = response.json()
                
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
                # Προσπάθεια 2: Αν είναι συμπιεσμένο/binary, καθαρίζουμε τα headers και επιστρέφουμε raw bytes
                resp_headers = dict(response.headers)
                resp_headers.pop("content-encoding", None)
                resp_headers.pop("content-length", None)
                resp_headers.pop("transfer-encoding", None)
                
                return Response(
                    content=response.content, 
                    status_code=response.status_code, 
                    headers=resp_headers
                )
                
    except Exception as e:
        # Προστασία από ολική πτώση σύνδεσης ή timeout
        return {"error": True, "message": f"Proxy upstream error: {str(e)}"}
