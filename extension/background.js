chrome.runtime.onInstalled.addListener(function(){
    const interval = setInterval(function() {
        var s = false;
        fetch('http://172.16.249.255:8000/blur')
            .then(response => response.text())
            .then(data => {if(data == 'True') {s = true;} else {s = false;} console.log(s);

        if(data =="True")
            {blur();}
            else
            {unBlur();}
    });
}, 2000);

});

function blur()
{
    chrome.tabs.insertCSS({file: "blur.css"});
}

function unBlur()
{
    chrome.tabs.insertCSS({file:"unblur.css"})
}