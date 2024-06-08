import modules.entities
import modules.db, modules.helpers
from aiohttp import web
import jinja2
from pathlib import Path
import asyncio, sys, json

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ROOT_DIR = Path(__file__).parent

env = modules.helpers.getEnv()

db = modules.db.Database(env.postgresConnectionString)

app = web.Application()
renderer = jinja2.Environment(loader=jinja2.FileSystemLoader(ROOT_DIR / 'templates'))

router = web.RouteTableDef()

sessions = []

@router.get('/')
async def web_root(request: web.Request):
    return web.Response(text='Yazaar Redirect App 2.0.0')

router.static('/static', ROOT_DIR / 'static')

@router.get('/admin')
async def web_admin(request: web.Request):
    modules.helpers.cleanSessions(sessions)
    session = modules.helpers.validateSession(sessions, request.cookies.get('session'))
    if not session:
        template = renderer.get_template('admin_locked.html')
        render = template.render()
        return web.Response(text=render, headers={'Content-Type': 'text/html'})
    
    redirects = await db.get_redirects()
    template = renderer.get_template('admin_unlocked.html')
    render = template.render(redirects=redirects)
    return web.Response(text=render, headers={'Content-Type': 'text/html'})

@router.post('/admin/auth')
async def web_admin_auth(request: web.Request):
    response = web.Response(headers={'Content-Type': 'application/json'})
    authorization = request.headers.get('authorization')
    if authorization == env.secret:
        session = modules.helpers.createSession()
        response.set_cookie('session', session.secret)
        sessions.append(session)
        respData = {'status': 'ok'}
    else:
        respData = {'status': 'reject'}
    response.text = json.dumps(respData)
    return response

@router.post('/admin/url/delete')
async def web_admin_url_set(request: web.Request):
    modules.helpers.cleanSessions(sessions)
    session = modules.helpers.validateSession(sessions, request.cookies.get('session'))
    if not session:
        respData = {
            'status': 'reject',
            'reason': 'invalid_session'
        }
        resp = web.Response(text=json.dumps(respData), headers={'Content-Type': 'application/json'})
        resp.del_cookie('session')
        return resp
    
    try:
        data = await request.json()
        if not isinstance(data, dict): raise Exception('Data not of type JSON object (dict)')
    except Exception:
        return web.Response(text=json.dumps({ 'status': 'reject', 'reason': 'invalid_data' }), headers={'Content-Type': 'application/json'})

    try: rId = int(data.get('editedId'))
    except Exception:
        return web.Response(text=json.dumps({ 'status': 'reject', 'reason': 'invalid_data_keys' }), headers={'Content-Type': 'application/json'})

    redirect = await db.get_redirect_by_id(rId)

    if not redirect:
        return web.Response(text=json.dumps({ 'status': 'reject', 'reason': 'invalid_id' }), headers={'Content-Type': 'application/json'})

    await db.delete_redirect(redirect)
    return web.Response(text=json.dumps({ 'status': 'ok' }), headers={'Content-Type': 'application/json'})

@router.post('/admin/url/set')
async def web_admin_url_set(request: web.Request):
    modules.helpers.cleanSessions(sessions)
    session = modules.helpers.validateSession(sessions, request.cookies.get('session'))
    if not session:
        respData = {
            'status': 'reject',
            'reason': 'invalid_session'
        }
        resp = web.Response(text=json.dumps(respData), headers={'Content-Type': 'application/json'})
        resp.del_cookie('session')
        return resp
    

    try:
        data = await request.json()
        if not isinstance(data, dict): raise Exception('Data not of type JSON object (dict)')
    except Exception:
        return web.Response(text=json.dumps({ 'status': 'reject', 'reason': 'invalid_data' }), headers={'Content-Type': 'application/json'})

    rPath = data.get('path')
    rType = data.get('type')
    rTarget = data.get('target')
    rId = data.get('editedId')
    if rId:
        try: rId = int(rId)
        except Exception: rId = ''

    if not modules.helpers.validateRedirect(rPath, rType, rTarget, rId):
        return web.Response(text=json.dumps({ 'status': 'reject', 'reason': 'invalid_data_keys' }), headers={'Content-Type': 'application/json'})

    if isinstance(rId, int):
        redirect = await db.get_redirect_by_id(rId)
        if not redirect:
            return web.Response(text=json.dumps({ 'status': 'reject', 'reason': 'invalid_id' }), headers={'Content-Type': 'application/json'})
        await db.update_redirect(redirect, rPath, rType, rTarget)
        return web.Response(text=json.dumps({ 'status': 'ok' }), headers={'Content-Type': 'application/json'})

    await db.set_redirect(rPath, rType, rTarget)
    return web.Response(text=json.dumps({ 'status': 'ok' }), headers={'Content-Type': 'application/json'})

@router.get('/{path:.+}')
async def web_redirects(request: web.Request):
    path = modules.helpers.flatPath(request.path)
    if path is None: return web.Response(text='invalid path')

    dbRedirect = await db.get_redirect_by_path(path)
    if not dbRedirect: return web.Response(text='path not registered')

    if dbRedirect.type == 'redirect':
        return web.Response(status=302, headers={'location': dbRedirect.target})
    
    if dbRedirect.type == 'download':
        template = renderer.get_template('background_download.html')
        resp = template.render({
            'title': 'download - Yazaar Redirect App 2.0.0',
            'download_url': dbRedirect.target,
            'wait_time_s': 5
        })
        return web.Response(text=resp, headers={'Content-Type': 'text/html'})
    return web.Response(text='invalid redirect type')

app.add_routes(router)

runner = web.AppRunner(app)
site = None

async def startup():
    global site
    if site: return
    await db.startup()
    await runner.setup()
    site = web.TCPSite(runner=runner, host='0.0.0.0', port=env.webPort)
    await site.start()
    while True:
        await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(startup())
