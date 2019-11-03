
$(document).ready(function(){
    $('#calibrate').click(function a(){
        fetch('https://poseright.ml/calibrate', {method: 'post'});
    });
});
