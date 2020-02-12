var myApp = angular.module('serversMgmt',[]);

// Get app version
myApp.controller("version", function($scope, $http){
	$http.get("api/version").then(function(response){
		$scope.version = response.data.version;
	});
});

myApp.controller("server-details", function($scope, $http){
	$scope.$on("display-server-details", function(evt, data){
		console.log("display server");
		$("#serverDetails").removeClass("hidden");
		$("#userDetails").addClass("hidden");
		$scope.getServerDetails(data);
	});

	$scope.getServerDetails = function(server) {
		console.log("%o", server);
		$http.get("api/servers/"+server.id).then(function(response){
			console.log("%o", response.data);
			$scope.address = response.data.server.address;
			$scope.server_id = response.data.server.id;
		});
		$http.get("api/servers/"+server.id+"/shares").then(function(response){
			console.log("%o", response.data);
			$scope.shares = response.data.shares;
		});
		$http.get("api/users").then(function(response){
			console.log("%o", response.data);
			$scope.users = response.data.users;
		});
	};

	$scope.addShare = function() {

		data = {
			"username" : $scope.username,
			"server_id" : $scope.server_id

		};
		$http.post("api/shares", data).then(function(response) {
			console.log("%o", response);
		});

		$('#addShareServer').modal('hide');
		$scope.getServerDetails({"id":$scope.server_id});
	};
});

myApp.controller("user-details", function($scope, $http){
	console.log("user loaded");
	$scope.$on("display-user-details", function(evt, data){
		console.log("user details");
		$("#userDetails").removeClass("hidden");
		$("#serverDetails").addClass("hidden");
	});
});

myApp.controller("certificat", function($scope, $http){
	$scope.getPubKey = function() {
		$http.get("api/certificates").then(function(response){
			$scope.public_key = response.data.certificates[0].public_key;
		});
	};

	$scope.generateCert = function() {
		$http.post("api/certificates").then(function(response){
			console.log("%o", response.data);
		});
	};

	$scope.getPubKey();
});

myApp.controller("users", function($scope, $http, $rootScope){

	

	$scope.getUsersList = function() {
		console.log("Get users list");

		$http.get("api/users").then(function(response){
			$scope.users = response.data.users;
			console.log("%o", response.data);
		});
	};


	$scope.displayDetails = function(user) {
		$rootScope.$broadcast("display-user-details", user);
	};

	$scope.deleteUser = function(user) {
		$http.delete("api/users/" + user.username).then(function(response){
			console.log("%o", response);
		});
		console.log("Remove " + user.username);
		$scope.getUsersList();
	};

	$scope.addUser = function() {

		data = {
			"username" : $scope.username

		};
		$http.post("api/users", data).then(function(response) {
			console.log("%o", response);
		});

		$('#addUser').modal('hide');
		$scope.getUsersList();
	};




	$scope.getUsersList();

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

myApp.controller("servers", function($scope, $http, $rootScope){

	

	$scope.getServersList = function() {
		console.log("Get servers list");

		$http.get("api/servers").then(function(response){
			$scope.servers = response.data.servers;
		});
	;}

	$scope.displayDetails = function(server) {
		console.log(server.address);
		$rootScope.$broadcast("display-server-details", server);
	};

	$scope.deleteServer = function(server) {
		$http.delete("api/servers/" + server.id).then(function(response){
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
