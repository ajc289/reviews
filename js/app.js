var phonecatApp = angular.module('phonecatApp', ['ui.bootstrap','ngRoute','phonecatControllers']);

phonecatApp.config(['$routeProvider',
   function ($routeProvider){
      $routeProvider.
         when('/search',{templateUrl: 'partials/search.html', controller: 'SearchCtrl'}).
         when('/search/:query',{templateUrl: 'partials/search_result.html', controller: 'SearchResultCtrl'}).
         when('/reviews/:product_code',{templateUrl: 'partials/review-detail.html', controller: 'ReviewDetailCtrl'}).
         otherwise({redirectTo: '/search'});
      }]);
