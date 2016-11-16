//On ready
$(function( ) {

//JSON data
	var exp = [
		{column: 0, id: "FutureAdvisor", sdate: new Date(2013, 11, 15), edate: new Date(2014, 6, 15)},
		{column: 1, id: "Statis", 'sdate': new Date(2012, 4, 15), edate: new Date()},
		{column: 0, id: "Premier Jet Center", sdate: new Date(2012, 11, 15), edate: new Date(2013, 9, 9)},
		{column: 0, id: "University of Minnesota", sdate: new Date(2009, 8, 1), edate: new Date(2012, 11, 15)},
		{column: 1, id: "International Business Association", sdate: new Date(2010, 4, 15), edate: new Date(2012, 4, 15)},
		//{column: 2, id: "Al-Madina Investment House", sdate: new Date(2011, 9, 1), edate: new Date(2011, 11, 15)},
		{column: 2, id: "Muscat Securities Market", sdate: new Date(2011, 8, 15), edate: new Date(2011, 10, 31)},
		{column: 2, id: "Shelter For Life International", sdate: new Date(2011, 4, 15), edate: new Date(2011, 7, 20)},
		{column: 2, id: "Pratt Elementary School", sdate: new Date(2009, 8, 15), edate: new Date(2011, 4, 1)},
		{column: 1, id: "Territorial Residence Hall Council", sdate: new Date(2009, 8, 25), edate: new Date(2010, 1, 28)}];


    $( "#work" ).on( "click", function( event ) {

    	event.preventDefault( );
        //mixpanel.track("#work click-capture");

        var href = "/work"
        $( "#tagline" ).fadeOut( 1500 );
        $( "#homepage" ).fadeOut( 1500 )
            .animate( {paddingTop: "25px"}, tlineClass );
        $( "#head-wrapper" ).fadeOut( 1500 )
            .animate( {top: "-= 120"}, tlineClass );
        $( "nav" ).fadeOut( 1500 )
            .animate( {bottom: "5%"}, tlineClass );
        //$( "#work" ).toggleClass( "hidden" );

    	if($( "#chart" ).length == 0) {
    		initTimeline();
    	}
    });

    $( "#direct-work" ).on( "click", function( event ) {

        //mixpanel.track("#work click-capture");
        $(document).ready(function() {
             $("#tagline").fadeOut(1500);
            $("#homepage").fadeOut(1500)
                .animate({paddingTop: "25px"}, tlineClass);
            $("#head-wrapper").fadeOut(1500)
                .animate({top: "-= 120"}, tlineClass);
            $("nav").fadeOut(1500)
                .animate({bottom: "5%"}, tlineClass);
            //$( "#work" ).toggleClass( "hidden" );

            if ($("#chart").length == 0) {
                initTimeline();
            }
        })
    });

	function tlineClass( ) {

        $( this ).addClass( "tline" );
        $( this ).fadeIn( 2000 );

    }

	function initTimeline( ) {

		var $chartTalk = $( "<div id=\"chart\" class=\"hidden\">" + "<div id=\"tooltip\">" + "<p><strong><span id=\"labelId\">Important Label Heading</span></strong></p>" + "<p><span id=\"value\">yes</span></p>" + "</div>" + "<div id=\"keyContainer\">" + "<ul id=\"chartKey\"></ul>" + "</div></div>" );
		$chartTalk.insertAfter( "header" );

		chartMachine();

		var $chart = $( "#chart" );
		$chart.delay( 2000 )
				.fadeIn( 2000 );

	}

	var browserH = $( window ).innerHeight();

	function chartMachine( ) {

		var columns = ["One", "Two", "Three"],
			numOfCol = columns.length,
			timeBegin = new Date(2009, 5, 1),
			timeEnd = new Date(2014, 11, 31);

		var margin = {top:10, right: 10, bottom: 10, left: 10},
			w = 200,
			h = (browserH * 0.85),
			barWidth = 45;

		var x = d3.scale.linear()
			.domain([0, numOfCol])
			.range([20, w]);

		var y = d3.time.scale()
			.domain([timeBegin, timeEnd])
			.range([h, 0]);

//create chart
		var chart = d3.select("#chart").insert("svg", "#keyContainer")
			.classed("chart", true)
				.attr("width", w + margin.left + margin.right)
				.attr("height", h + margin.top + margin.bottom)
			.append("g")
				.attr("class", "g_main")
				.attr("transform", "translate(-10,-10)");

		var keyHeight = [];
		keyHeight = function( exp ) { return exp.edate; };

		var chartKey = d3.select("#chartKey").selectAll("li")
				.data(exp)
			.enter().append("li")
			.attr("id", function(d, i) { return "li-" + i; })
			.text(function(d) { return d.id; })
			.style("position", "absolute")
			.style("top", function(d) { return y(d.edate) + 'px'; })
			.style("left", function() { return 0 + 'px'; });

		d3.select('#li-5')
			.style('top', function() { return y(exp[5].edate) + 14 + 'px'; });
		d3.select('#li-4')
			.style('top', function() { return y(exp[4].edate) - 1 + 'px'; });
		d3.select('#li-1')
			.style('top', function() { return y(exp[1].edate) + 60 + 'px'; });


		var sdate = d3.time.format('%Y-%m-%d');

		var coordinates = [0, 0];
		var mouseX = coordinates[0];
		var mouseY = coordinates[1];

//create bars
		chart.append("g").selectAll("rect")
				.data(exp)
			.enter().append("rect")
				.attr("class", function(d) { return "rect" + d.column; })
			.attr("id", function(d) { return d.id; })
			.attr("class", function(d) { return sdate(d.sdate); })
			.attr("x", function(d) { return x(d.column); })
			.attr("y", function(d) { return y(d.edate); })
			.attr("width", barWidth)
			.attr("height", function(d) { return y(d.sdate) - y(d.edate); })
			.attr('rx', 5)
			.attr('ry', 5);

//Animations when hovering over bar
		chart.selectAll('rect')
			.on("mouseover", function(d, i) {

//Highlight bar when hovering
				d3.select(this)
					.style({'fill': '#ff9966','fill-opacity': '.8'});

				d3.select('#li-' + i)
					.style('color', '#E5692C');

				d3.select('#keyLine-' + i)
					.style({'stroke': '#ff9966', 'stroke-opacity': 0.8});

//Get this bar's x/y values, then augment for the tooltip
				var xPosition = parseFloat(d3.select(this).attr("x")) + x / 2;
				var yPosition = parseFloat(d3.select(this).attr("y")) / 1 + h/4;

//Update the tooltip position and value
				d3.select("#tooltip")
  					.style({"left": xPosition,
  							"top": function(d) { return yPosition + "px"; }})
  					.select("#labelId")
  					.text(d.id)
  					.select("#value")
  					.text(d.id);
  			});

//Exit hover
		chart.selectAll('rect')
			.on("mouseout", function(d, i) {

//Exit highlight
				d3.select(this).transition()
					.duration(600)
					.style({'fill': '#ff9966','fill-opacity': '0.5'});

				d3.select('#li-' + i)
					.style('color', '#232323');

				d3.select('#keyLine-' + i)
					.style({'stroke': '#ff9966', 'stroke-opacity': 0.2});
			});

//Animations when hovering over chartkey
		d3.select('#chartKey').selectAll('li')
			.on("mouseover", function(d, i) {

//Highlight bar when hovering
				d3.select(this)
					.style('color', '#E5692C');

				d3.select('#' + d.id)
					.style({'fill': '#ff9966','fill-opacity': '.8'});

				d3.select('#keyLine-' + i)
					.style({'stroke': '#ff9966', 'stroke-opacity': 0.8});
			});

//Exit highlight
		d3.select('#chartKey').selectAll('li')
			.on("mouseout", function(d, i) {

				d3.select('rect')
					.transition()
					.duration(600)
					.style({'fill': '#ff9966','fill-opacity': '0.5'});

				d3.select(this)
					.style('color', '#232323');

				d3.select('#keyLine-' + i)
				.style({'stroke': '#ff9966', 'stroke-opacity': 0.2});
			});

//Create timeline y-ticks
		chart.selectAll('line')
				.data(d3.range(2009, 2015))
			.enter().append('line')
				.attr('class', 'axis tick')
			.attr('x1', -5)
			.attr('y1', function (d) { return y(new Date(d, 0, 1)); })
			.attr('x1', -5)
			.attr('y2', function (d) { return y(new Date(d, 0, 1)); })
			.style("stroke", "#F5F5F5");

//Create date labels
		chart.selectAll('.rule')
				.data(d3.range(2009, 2015))
			.enter().append('text')
				.attr('class', 'rule')
			.attr('x', -60)
			.attr('y', function (d) { return y(new Date(d, 0, 1)); })
			.attr('dy', -5)
			.attr('text-anchor', 'left')
			.text(function (d) { return d; })
			.style('pointer-events', 'none');

//Create timeline y-axis
		chart.append('line')
	 			.attr('class', 'axis domain')
	 		.attr('y1', y(timeBegin))
	 		.attr('y2', y(timeEnd))
	 		.style('stroke', '#F5F5F5');

		/*d3.select('svg').selectAll('.keyLine')
				.data(exp)
			.enter().append('line')
				.attr('id', function(d, i) { return 'keyLine-' + i; })
			.attr('x1', function(d) { return x(d.column) + margin.left; })
			.attr('y1', function(d) { return y(d.edate) + margin.top + 1; })
			.attr('x2', 150)
			.attr('y2', function(d) { return y(d.edate) + margin.top + 1; })
			.style({'z-index': 100000, 'stroke': '#ff9966', 'stroke-opacity': 0.2});*/
	}
});


/*chart
	.on('mousemove', function() {
		cx = d3.mouse(this)[0];
		cy = d3.mouse(this)[1];
		console.log("xx=>" + cx + "yy=>" + cy);
		redrawline(cx, cy);
	})
	.on('mouseover', function() {
		d3.selectAll('.line_over')
			.style('display', 'block');
	})
	.on('mouseout', function() {
		d3.selectAll('.line_over')
			.style('display', 'none');
	})
	.append("rect")
		.attr('class', 'click-capture')
		.style('visibility', 'hidden')
		.attr('x', 0)
		.attr('y', 0)
		.attr('width', w)
		.attr('height', h);

//console.log(this);
chart.append('line')
//d3.select("svg").append("line")
		.attr('class', 'line_over')
    	.attr("x1", 0)
    	.attr("y1", 0)
    	.attr("x2", 395)
    	.attr("y2", 0)
    	.style('stroke', '#c2c2c2')
    	.attr('stroke', ('5,5'))
    	.style('stroke-width', '1')
    	.style('display', 'none');

function redrawline(cx, cy) {
	d3.selectAll('.line_over')
        .attr("x1", 0)
        .attr("y1", cy)
        .attr("x2", 395)
        .attr("y2", cy)
        .style("display", "block");
    }*/
