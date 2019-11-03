
$(document).ready(function() {
$('#blur').click(function blur()
{
    chrome.tabs.insertCSS({file: "blur.css"});
});
});

$(document).ready(function(){
    $('#unblur').click(function unBlur()
    {
        chrome.tabs.insertCSS({file:"unblur.css"})
    });
});
