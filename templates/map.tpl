% include('templates/header.tpl')

    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type='text/javascript'>
     google.load('visualization', '1', {'packages': ['geochart']});
     google.setOnLoadCallback(drawRegionsMap);

      function drawRegionsMap() {
        var chart = new google.visualization.GeoChart(document.getElementById('map_div'));
        var options = {
        	colors: ['#FFF', '#4374E0']
        };

        function getData() {
          $.ajax({
            url: '/lbstats/gettopcountries?group={{group}}',
            dataType: "json",
            async: false,
            success: function(response){
                data = google.visualization.arrayToDataTable(response);
                chart.draw(data, options);
                setTimeout(getData, 5000);
            },
            error: function(xhr, ajaxOptions, thrownError){
              setTimeout(getData, 10000);
            }
          });
        }
        getData();
    };
    </script>
    <div style="width: 90%; margin-left: auto; margin-right: auto;">
    	<div id="map_div"></div>
	</div>

% include('templates/footer.tpl')
