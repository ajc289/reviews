var phonecatControllers = angular.module('phonecatControllers', []);
 
phonecatControllers.controller('ReviewListCtrl', ['$scope', '$http', function ($scope, $http) {
$http.get('json/res2.json').success(function(data){
$scope.reviews = data;
});

}]);

phonecatControllers.controller('SearchTestCtrl', ['$scope', '$http', function ($scope, $http) {

$scope.query = '';

  var i =0;
  var images = ['http://www.sparkawards.com/galleries/archive/Butternut_Mato_ID_FrontRightOpen_LinenWhite_IFContest.jpg','http://images.amazon.com/images/G/01/electronics/sony/sony-12q4-Eseries-14-white-cover-lg.jpg','http://images.amazon.com/images/G/01/electronics/sony/sony-12q4-Eseries-11-white-duo-lg.jpg'];
  var image = $('#slideit');

  image.css('background-image', 'url(http://www.sparkawards.com/galleries/archive/Butternut_Mato_ID_FrontRightOpen_LinenWhite_IFContest.jpg)');

  setInterval(function(){
   image.css('background-image', 'url(' + images [i++] +')');

   if(i == images.length)
    i = 0;
  }, 5000);

$scope.new_search_query = function(){
   document.getElementById('search_form').action = 'http://www.igniipotent.com/reviews/angular-reviews/app/index.html?#/search_test/' + $scope.query.replace(/ /g, ';');
   document.getElementById('search_form').submit();
}
}]);

phonecatControllers.controller('SearchResultCtrl', ['$scope', '$routeParams', '$http',
function($scope, $routeParams, $http) {

   $http.get('/search?query=' + $routeParams.query).success(function(data){
   $scope.search_results = data;
   });


$scope.new_search_query = function(){
   document.getElementById('search_form').action = 'http://www.igniipotent.com/reviews/angular-reviews/app/index.html?#/search_test/' + $scope.query.replace(/ /g, ';');
   document.getElementById('search_form').submit();
}
}]);

phonecatControllers.controller('ReviewDetailCtrl', ['$scope', '$routeParams', '$http', '$sce',
function($scope, $routeParams, $http, $sce) {
$http.get('json/' + $routeParams.product_code + '.json').success(function(data) {
$scope.review = data;

feature_list = $scope.review['features'];

for (var i = 0; i < feature_list.length; i++)
{
   var new_html = "<span style=\"background-color:yellow;\">" + feature_list[i]['feature_name'] + "</span>";
   var re = new RegExp (feature_list[i]['feature_name'], 'g');
   for (var j = 0; j < feature_list[i]['feature_text'].length; j++)
   {
      feature_list[i]['feature_text'][j] = feature_list[i]['feature_text'][j].replace(re,new_html);
   }

   feature_list[i]['feature_curr_text'] = feature_list[i]['feature_curr_text'].replace(re,new_html);
}

});

$scope.open_in_tab = function(){
   var win = window.open($scope.review['page_url'], '_blank');
   win.focus();
};


$scope.to_trusted = function(html){

   return $sce.trustAsHtml (html);

};

$scope.inc_curr_text = function(feature_name){

feature_list = $scope.review['features'];

for (var i = 0; i < feature_list.length; i++)
{
   if (feature_list[i]['feature_name'] == feature_name)
   {
      if (feature_list[i]['feature_curr_text_index'] + 1 < feature_list[i]['feature_text'].length)
      {
         feature_list[i]['feature_curr_text_index'] += 1;
         var curr_index = feature_list[i]['feature_curr_text_index'];
         feature_list[i]['feature_curr_text'] = feature_list[i]['feature_text'][curr_index];
      }
   }
}

};

$scope.dec_curr_text = function(feature_name){

feature_list = $scope.review['features'];

for (var i = 0; i < feature_list.length; i++)
{
   if (feature_list[i]['feature_name'] == feature_name)
   {
      if (feature_list[i]['feature_curr_text_index'] - 1 >= 0)
      {
         feature_list[i]['feature_curr_text_index'] -= 1;
         var curr_index = feature_list[i]['feature_curr_text_index'];
         feature_list[i]['feature_curr_text'] = feature_list[i]['feature_text'][curr_index];
      }
   }
}

};
}]);
