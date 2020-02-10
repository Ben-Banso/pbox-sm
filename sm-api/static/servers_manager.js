var myApp = angular.module('serversMgmt',[]);

// Get app version
myApp.controller("version", function($scope, $http){
	$http.get("api/version").then(function(response){
		$scope.version = response.data.version;
	});
});


myApp.controller("external", function($scope, $http){

	

	$scope.getNodesList = function() {
		console.log("Get nodes list");

		$http.get("api/nodes").then(function(response){
			$scope.nodes = response.data.nodes;
		});
	;}


	$scope.getNodesList();

});

myApp.controller("servers", function($scope, $http){

	

	$scope.getServersList = function() {
		console.log("Get servers list");

		$http.get("api/servers").then(function(response){
			$scope.servers = response.data.servers;
		});
	;}

	$scope.deleteServer = function(server) {
		$http.delete("api/servers/" + server.address).then(function(response){
			console.log("%o", response);
		});
		console.log("Remove " + server.address);
		$scope.getServersList();
	};

	$scope.submitForm = function() {

		if($scope.authMethod == "key") {
			secret = $scope.key;
		}
		else if ($scope.authMethod == "password") {
			secret = $scope.password;
		}

		data = {
			"address" : $scope.serverAddress,
			"method" : $scope.authMethod,
			"user" : $scope.username,
			"secret" : secret

		};
		$http.post("api/servers", data).then(function(response) {
			console.log("%o", response);
		});
		console.log("submit form %o" , data);

		$('#addServer').modal('hide');
		$scope.getServersList();
	};

	$scope.getServersList();

});


myApp.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[').endSymbol(']]');
});

$(document).ready( function() {
	var method = $('#addServerForm select');
	var username = $('#username').parent().parent();
	var password = $('#password').parent().parent();
	var sshkey = $('#key').parent().parent();

	method.change( function() {
		var value = this.value;

		if(value == "password") {
			username.removeClass('hidden');
			password.removeClass('hidden');
			sshkey.addClass('hidden');
		}
		else if  (value == "key") {
			username.removeClass('hidden');
			password.addClass('hidden');
			sshkey.removeClass('hidden');
		}
	});

});
