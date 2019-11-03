
$(document).ready(function(){
    $('#calibrate').click(function a(){
        fetch('http://172.16.249.255:8000/calibrate', {method: 'post'});
    });
});
