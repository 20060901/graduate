window.onload = function () {
    var oDiv = document.getElementById('div1');//获取对象
    oDiv.onmouseover = function () {//给对象绑定事件
        startMove();
    }
    oDiv.onmouseout = function () {
        startMove1();
    }
}
var timer = null;//声明定时器先为空
function startMove() {
    clearInterval(timer);//进入函数执行定时器之前先清除所有的定时器
    var oDiv = document.getElementById('div1');
    timer = setInterval(function () {
        if (oDiv.offsetWidth == 280) { //如果当前对象left值为0也就是已经展开的状态
            clearInterval(timer);//那么就清除定时器，也就是停止运动
        } else {
            oDiv.style.width = oDiv.offsetWidth + 10 + 'px';//否则就从-200一直没个30ms加10像素一直到0为止
        }
    }, 30)
}

function startMove1() {//移出函数原理与移入相同
    clearInterval(timer);
    var oDiv = document.getElementById('div1');
    timer = setInterval(function () {
        if (oDiv.offsetWidth == 50) {//如果对象当前left值为-200也就是收起状态
            clearInterval(timer);//那么就清除定时器
        } else {
            oDiv.style.left = oDiv.offsetWidth - 10 + 'px';//否则就执行元素从0一直减10像素一直到-200为止
        }
    }, 30)

}