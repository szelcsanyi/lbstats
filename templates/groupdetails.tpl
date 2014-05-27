% include('templates/header.tpl')

<div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-dialog">
   <div class="modal-content">Loading...</div>
  </div>
 </div>

 <h1>Statistics for {{group}}</h1>
 % for host,val1 in stats.iteritems():
  <div class="row">
   <h2>{{host}}</h2>
   <div class="col-md-3">
    <ul class="list-group">
    % for i in val1['ips']:
     <li class="list-group-item">
      <span class="badge">{{i[1]}}</span><a data-toggle="modal" href="/lbstats/ips?ip={{i[0]}}&host={{host}}&group={{group}}" data-target="#myModal">{{i[0]}}</a>
     </li>
    % end
    </ul>
   </div>

   <div class="col-md-6">
    <ul class="list-group">
    % for i in val1['urls']:
     <li class="list-group-item">
      <span class="badge">{{i[1]}}</span><a data-toggle="modal" href="/lbstats/urls?url={{i[0]}}&host={{host}}&group={{group}}" data-target="#myModal">{{i[0]}}</a>
     </li>
    % end
    </ul>
   </div>

   <div class="col-md-3">
    <ul class="list-group">
    % for i in val1['countries']:
     <li class="list-group-item">
      <span class="badge">{{i[1]}}</span>{{i[0][0]}}
     </li>
    % end
    </ul>
   </div>

  </div><!-- row end -->
 %end

% include('templates/footer.tpl')
