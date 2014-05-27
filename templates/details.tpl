% include('templates/header.tpl')

<script type="text/javascript" src="https://www.google.com/jsapi"></script>
% for group in groups:
 <div class="row">
  <div class="col-md-4">
   <h3>{{group}}</a></h3>
    <a href="/lbstats/map?group={{group}}" class="btn btn-primary btn-sm"><span class="glyphicon glyphicon-globe"></span> Map</a>
    <a href="/lbstats/details?group={{group}}" class="btn btn-primary btn-sm"><span class="glyphicon glyphicon-zoom-in"></span> Details</a>
  </div>

  <div class="col-md-8">
   <div id="chart_reqps_{{group}}" style=" height: 100px;"></div>
  </div>
 </div>
 <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var chart = new google.visualization.AreaChart(document.getElementById('chart_reqps_{{group}}'));

        var options = {
          legend: { position: 'none'},
          chartArea:{left: 50, top: 10, width: "85%", height:"80%"},
          vAxis: {
           viewWindow:{
                min:0
              }
          }
        };

        function getData() {
          $.ajax({
            url: '/lbstats/getreqpshistory?group={{group}}',
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
      }
 </script>
% end

% include('templates/footer.tpl')
