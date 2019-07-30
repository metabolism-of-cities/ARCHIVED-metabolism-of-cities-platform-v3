  $(".main").onepage_scroll({
     sectionContainer: "section",     // sectionContainer accepts any kind of selector in case you don't want to use section
     easing: "ease",                  // Easing options accepts the CSS3 easing animation such "ease", "linear", "ease-in",
     animationTime: 800,              // AnimationTime let you define how long each section takes to animate
     loop: false,                     // You can have the page loop back to the top/bottom when the user navigates at up/down on the first/last page.
     keyboard: true,                  // You can activate the keyboard controls
     responsiveFallback: 992,
  });

  $(".changing.cities, .changing.success").cycleText({
    "interval": 2500,
    "animation": "fadeInUp"
  });

  $(".section.do-what .panel").mouseover(function() {
    var panelClass = $(this).attr("panelClass");
    $(".section.do-what .split-text").hide()
    $(".section.do-what .split-text." + panelClass).show();
    $(".section.do-what .split").addClass("darker");
    var backgroundColor = $(this).css("background-color")
    $(".section.do-what .split").css("background-color", backgroundColor);
  });

  $(".section.for-whom .panel").mouseover(function() {
    var panelClass = $(this).attr("panelClass");
    $(".section.for-whom .split-text").hide()
    $(".section.for-whom .split-text." + panelClass).show();
    $(".section.for-whom .split").addClass("darker");
    var backgroundColor = $(this).css("background-color")
    $(".section.for-whom .split").css("background-color", backgroundColor);
  });

  $(".section.do-what .row.panel-collection").mouseleave(function() {
    $(".section.do-what .split-text:visible").fadeOut(200, function(){
      $(".section.do-what .split-text.standard").fadeIn(200);
    })
  });

  /*$(".section.for-whom .row.panel-collection").mouseleave(function() {
    $(".section.for-whom .split-text:visible").fadeOut(200, function(){
      $(".section.for-whom .split-text.standard").fadeIn(200);
    })
  });*/

  $(".downArrow").click(function() {
    $(".main").moveDown();
  })
