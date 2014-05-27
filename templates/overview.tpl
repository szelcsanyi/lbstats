% include('templates/header.tpl')

 <div class="row">

  <div class="col-md-3">
   <div class="panel panel-primary">
    <div class="panel-heading">Requests per sec</div>
    <div class="panel-body text-center" id="reqps">
     <h1>0</h1>
    </div>
   </div>
  </div>

  <div class="col-md-3">
   <div class="panel panel-primary">
    <div class="panel-heading">Requests in buffer</div>
    <div class="panel-body text-center" id="requests" >
     <h1>0</h1>
    </div>
   </div>
  </div>

 </div>


 <script type="text/javascript" src="https://www.google.com/jsapi"></script>

    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var chart = new google.visualization.LineChart(document.getElementById('chart_reqps'));

        var options = {
          title: 'Request/s',
          curveType: 'function',
          legend: { position: 'top', maxLines: 2 },
          chartArea:{left: 50, top: 60, width: "85%", height:"75%"},
          vAxis: {
           viewWindow:{
                min:0
              }
          }
        };

        function getData() {
          $.ajax({
            url: '/lbstats/getreqpshistory',
            dataType: "json",
            async: false,
            success: function(response){
                data = google.visualization.arrayToDataTable(response);
                chart.draw(data, options);
                setTimeout(getData, 2000);
            },
            error: function(xhr, ajaxOptions, thrownError){
              setTimeout(getData, 10000);
            }
          });
        }
        getData();
      }
    </script>


    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var chart = new google.visualization.PieChart(document.getElementById('chart_domains'));

        var options = {
          title: 'Domains',
          legend: { position: 'top', maxLines: 2 },
          pieHole: 0.4,
          chartArea:{left: 10, top: 60, width: "75%", height:"75%"},
          colors: ['#4374E0', '#4285F4', '#76A7FA', '#A0C3FF'],
        };

        function getData() {
          $.ajax({
            url: '/lbstats/gettopdomains',
            dataType: "json",
            async: false,
            success: function(response){
                data = google.visualization.arrayToDataTable(response);
                chart.draw(data, options);
                setTimeout(getData, 10000);
            },
            error: function(xhr, ajaxOptions, thrownError){
              setTimeout(getData, 10000);
            }
          });
        }
        getData();
      }
    </script>


 <div class="row">
  <div class="col-md-8">
    <div id="chart_reqps" style="width: 700px; height: 300px;"></div>
  </div>
  <div class="col-md-4">
    <div id="chart_domains" style="width: 300px; height: 300px;"></div>
  </div>
 </div>


 <script>
 function getStatus() {
 
    $.getJSON('/lbstats/getcounters', 
      function(data) {
        $('div#reqps').html("<h1>" + data['reqps'] + "</h1>");
        $('div#requests').html("<h1>" + data['requests'] + "</h1>");
      }
    );
    setTimeout("getStatus()", 1000);
 
 }

 $(document).ready(function(){ getStatus(); });
 </script>

% include('templates/footer.tpl')
