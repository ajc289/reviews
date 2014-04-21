var phonecatApp = angular.module('phonecatApp', ['ui.bootstrap','ngRoute','phonecatControllers']);

phonecatApp.config(['$routeProvider',
   function ($routeProvider){
      $routeProvider.
         when('/search_test',{templateUrl: 'partials/search_test.html', controller: 'SearchTestCtrl'}).
         when('/search_test/:query',{templateUrl: 'partials/search_result.html', controller: 'SearchResultCtrl'}).
         when('/reviews',{templateUrl: 'partials/review-list.html', controller: 'ReviewListCtrl'}).
         when('/reviews/:product_code',{templateUrl: 'partials/review-detail.html', controller: 'ReviewDetailCtrl'}).
         when('/phones',{templateUrl: 'partials/phone-list.html', controller: 'PhoneListCtrl'}).
         when('/phones/:phoneId',{templateUrl: 'partials/phone-detail.html', controller: 'PhoneDetailCtrl'}).
         otherwise({redirectTo: '/phones'});
      }]);
