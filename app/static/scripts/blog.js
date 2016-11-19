$(function() {

/*    var content = '<form action="'+$SCRIPT_ROOT+'/auth/subscribe" method="post" id="mc-embedded-subscribe-form" name="mc-embedded-subscribe-form" class="validate"><div id="mc_embed_signup_scroll"><input type="email" value="" name="EMAIL" class="email" id="mce-EMAIL" placeholder="email address" required><div style="position: absolute;left: -5000px;"><input type="text" name="b_1c77aa72613dcb897013178e1_3c734f704d" tabindex="-1" value=""></div><div class="clear"><input type="submit" value="Submit" name="subscribe" id="mc-embedded-subscribe" class="button"></div></form>';

    var fullUrl = window.location.href;
    var parsedUrl = $.url(fullUrl);
    var parser = new UAParser();

    var eventProperties = {
        user_agent: {
            browser: parser.getBrowser(),
            engine: parser.getEngine(),
            os: parser.getOS()
        },
        permanent_tracker: $.cookie("permanent_cookie")["id"]
    }
        
    var referrer = document.referrer;
    referrerObject = null;

    if(referrer != undefined){
        parsedReferrer = $.url(referrer);
        referrerObject = {
            source: parsedReferrer.attr("source"),
            protocol: parsedReferrer.attr("protocol"),
            domain: parsedReferrer.attr("host"),
            port: parsedReferrer.attr("port"),
            path: parsedReferrer.attr("path"),
            anchor: parsedReferrer.attr("anchor")
        }
    }
    eventProperties["referrer"] = referrerObject;
    $("#mc-embedded-subscribe").on('click', function(e) {
        client.addEvent("subscribing", eventProperties)
        $("#mc_landing_signup").html(content)
    })
    $("#mc-embedded-subscribe").on('click', function(e) {
        client.addEvent("subscribing", eventProperties)
        $("#mc_embed_signup").html(content)
    })*/

    $('#topics').on('click', '.topic-control', function(e){
        e.preventDefault();
        $(this)
            .next('.topic-panel')
            .not(':animated')
            .slideToggle();
        var displayStatus = $(this).css('display');
        if(displayStatus == 'block') {
            $('.topic-control').css('background-color', '#999999');
        } else {
            $('.topic-control').css('background-color', '#fffdff');
        }
    });
});
