<html>
<body>
<ul class="list-group">
% for i in items:
	<li class="list-group-item">
	<span class="badge">{{i[1]}}</span>{{i[0]}}
	</li>
% end
</ul>
</body>
</html>
