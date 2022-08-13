from flask import Flask, jsonify, request, send_file
import dd_query
import io
import os
import shutil

app = Flask(__name__)
spath = os.path.split(__file__)[0]


@app.route('/')
def index():
    return '答案是跑起来了！'


@app.route('/chachengfen/<path:username>')
def chachengfen(username):
    query_user = username

    # 定义不同的返回文本
    def ret_stat(status_code: int, msg: str):
        return {
            "stat": status_code,
            "text": msg
        }

    try:  # 错误捕获
        dd = dd_query.DDImageGenerate(query_user, max_follow_list=2000)
    except dd_query.errors.UserBan:
        return jsonify(ret_stat(1, "用户关注列表已设置为隐私，无法查看。"))
    except dd_query.errors.APIError:
        return jsonify(ret_stat(3, "用户信息拉取失败。"))
    except dd_query.errors.UserNotFound:
        return jsonify(ret_stat(2, "未找到此用户。"))
    except BaseException as e:
        return jsonify(ret_stat(5, f"服务器内部错误: {repr(e)}"))

    image_path, vtb_following_count, total_following_count = dd.image_generate()
    if not os.path.isdir(f"{spath}\\output"):
        os.makedirs(f"{spath}\\output")
    shutil.move(image_path, f"{spath}\\output\\{username}.jpg")
    json_r = {
        "stat": 200,
        "image_url": request.url_root + f"output/{username}.jpg",  # request.url_root: http://x.x.x.x:xxxx/
        "vtbcount": vtb_following_count,
        "count": total_following_count
    }
    return jsonify(json_r)


@app.route('/output/<path:imageid>')
def getimage(imageid):
    with open(f"output/{imageid}", "rb") as fi:
        return (send_file(
            io.BytesIO(fi.read()),
            mimetype='image/jpeg'
        ), 200)
