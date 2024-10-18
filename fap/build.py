#!/usr/bin/python3

import json
import websocket  # websocket_client

cogname = 'fap'

if not cogname:
    raise Exception('Set cogname in build.sh script!')

ws = websocket.create_connection(f'ws://localhost:6133')
mess = '{"jsonrpc": "2.0", "method": "CORE__RELOAD", "params": [["%s"]], "id": "%s"}' % (cogname, 'some_id')
ws.send(mess)
print(json.dumps(json.loads(ws.recv()), indent=4))
ws.close()
