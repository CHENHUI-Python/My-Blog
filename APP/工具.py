import os
import PIL
from PIL  import Image
from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect, current_app,flash


def is_safe_url(target): #安全【返回当前页面 1】
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs): #返回当前页面 2
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))



def resize_image(image,filename,base_width):      #剪裁上传的图片（参数：文件，文件名，尺寸）在其他视图调用次函数后，传入的实参依次对应形参
    filename,ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] <= base_width:                 #首先判断图片的大小，是否小于要设置的宽度
        return filename + ext                     #如果小于则不用剪裁，直接返回源文件的文件名
    w_percent = (base_width / float(img.size[0])) #接着根据图片的设置宽度，对图片进行缩小处理
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width,h_size), PIL.Image.ANTIALIAS)

    #文件名中的后缀将通过“宽度值”作为键，从配置变量中获取
    filename = filename + current_app.config['ALBUMY_PHOTO_SUFFIX'][base_width] + ext
    #接着将图片保存到上传文件夹，并返回文件名                                     优化（是否压缩） = True      质量 = 85
    img.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'],filename), optimize = True, quality = 85)
    return filename


def flash_errors(form): #闪现错误信息
    for field, errors in form.errors.items():
        for error in errors:
            flash(" %s 字段中的错误 %s" % (getattr(form, field).label.text,error))