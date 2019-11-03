
$(document).ready(function() {
$('#blur').click(function blur()
{
    chrome.tabs.insertCSS({file: "blur.css"});
    //document.body.style.filter = "blur(10px)";
    alert("FUCK"); 
});
});

$(document).ready(function(){
    $('#unblur').click(function unBlur()
    {
        chrome.tabs.insertCSS({file:"unblur.css"})
    });
});

/*function blur()
{
    document.body.style.filter = "blur(10px)";
}

function unBlur()
{
    document.body.style.filter = "blur(0px)";
}
*/