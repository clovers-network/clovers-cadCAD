import requests
import os
import json
import base64

api_url = 'https://jupyterhub.giveth.io/user/brennekamp/api'
auth_header = {
    'Authorization': 'token %s' % os.environ['JUPYTER_API_TOKEN'],
}

source_dir = './src'

def parse_dir_result(result):

    for f in result['content']:
        r = requests.get(api_url + '/contents/' + f['path'],
            headers=auth_header
            )

        r.raise_for_status()
        res = r.json()


        if res['type'] == 'directory':
            print("Making directory %s in src/%s" % (res['name'], res['path']))
            os.makedirs(source_dir + '/' + res['path'], exist_ok=True)

            parse_dir_result(res)
        else:
            print("Saving file %s to src/%s" % (res['name'], res['path']))

            if res['format'] == 'json':
                content = json.dumps(res['content'], indent=1)
                writeMode = "w"
            elif res['format'] == 'text':
                content = res['content']
                writeMode = "w"
            elif res['format'] == 'base64':
                b = bytes(res['content'], 'utf-8')
                content = base64.decodebytes(b)
                writeMode = "wb"
            else:
                raise(Exception("Unrecognized format '%s' for writing to file %s" % (res['format'], res['path'])))

            f = open(source_dir + '/' + res['path'], writeMode)
            f.write(content)
            f.close()

r = requests.get(api_url + '/contents',
    headers=auth_header
    )

r.raise_for_status()
root_directory = r.json()

parse_dir_result(root_directory)


