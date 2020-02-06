var myApp = angular.module('serversMgmt',[]);

myApp.controller("version", function($scope, $http){
	$http.get("api/version").then(function(response){
		$scope.version = response.data.version;
	});
});
myApp.controller("servers", function($scope, $http){
	$http.get("api/servers").then(function(response){
		$scope.servers = response.data.servers;
	});
});
myApp.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[').endSymbol(']]');
});
