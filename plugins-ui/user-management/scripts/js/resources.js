define([
    'angular',
    'angular-resource'
],function(angular) {
    'use strict';

    var resources = angular.module('users.resources', ['ngResource']);

    resources.factory('Role', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/RBAC/Role/:Id/:Action', {Id: '@Id', Action: '@Action'}, {
            query: {method: 'GET', params: {'X-Filter': '*'}},
            update: {method: 'PUT'},
            save: {method: 'POST', params: {'X-Filter': 'Id'}}
        });
    }]);

    resources.factory('User', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/HR/User/:Id/:Action/:Action2', {Id: '@Id', Action: '@Action', Action2: '@Action2'}, {
            query: {method: 'GET', params: {'X-Filter': '*'}},
            update: {method: 'PUT'},
            save: {method: 'POST', params: {'X-Filter': 'Id'}}
        });
    }]);
    
    resources.factory('UserRole', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/HR/User/:Id/Role', {Id: '@Id'}, {
            query: {method: 'GET', params: {'X-Filter': '*'}},
            update: {method: 'PUT'},
            save: {method: 'POST', params: {'X-Filter': 'Id'}}
        });
    }]);

    resources.factory('Post', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/HR/User/:Id/Post', {Id: '@Id'}, {
            query: {method: 'GET', params: {'X-Filter': '*'}}
        });
    }]);

    resources.factory('PostPublished', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/HR/User/:Id/Post/Published', {Id: '@Id'}, {
            query: {method: 'GET', params: {'X-Filter': '*'}}
        });
    }]);

    resources.factory('PostUnpublished', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/HR/User/:Id/Post/Unpublished', {Id: '@Id'}, {
            query: {method: 'GET', params: {'X-Filter': '*'}}
        });
    }]);

    resources.factory('UserDetailLoader',
    ['User', 'UserRole', 'Post', 'PostPublished', 'PostUnpublished', '$q',
    function(User, UserRole, Post, PostPublished, PostUnpublished, $q) {
        return function(userId) {
            var delay = $q.defer();
            User.query({Id: userId}, function(user) {
                UserRole.query({Id: userId}, function(role) {
                    user.roleList = role.RoleList;
                    Post.query({Id: userId}, function(post) {
                        user.postList = post.PostList;
                        PostPublished.query({Id: userId}, function(postPublished) {
                            user.postPublishedList = postPublished.PostList;
                            PostUnpublished.query({Id: userId}, function(postUnpublished) {
                                user.postUnpublishedList = postUnpublished.PostList;
                                delay.resolve(user);
                            });
                        });
                    });
                });
            });
            return delay.promise;
        };
    }]);

    resources.factory('UserListLoader', ['User', '$q', function(User, $q) {
        return function(offset, limit, searchTerm) {
            var delay = $q.defer();
            var parameters = {offset: offset, limit: limit};
            if (searchTerm !== undefined && searchTerm !== '') {
                parameters['all.ilike'] = searchTerm;
            }
            User.query(parameters, function(response) {
                for (var i = 0; i < response.UserList.length; i = i + 1) {
                    response.UserList[i].checked = false;
                }
                response.UserList.count = response.total;
                delay.resolve(response.UserList);
            });
            return delay.promise;
        };
    }]);

    resources.factory('RoleListLoader', ['Role', '$q', function(Role, $q) {
        return function() {
            var delay = $q.defer();
            var parameters = {};
            Role.query(parameters, function(response) {
                delay.resolve(response.RoleList);
            });
            return delay.promise;
        };
    }]);

    resources.service('UserService', ['$resource', '$q', function($resource, $q) {
        var UserImage = $resource('/resources/HR/Person/:userId/MetaData/Icon', {userId: '@userId'});

        this.getImage = function(user) {
            var delay = $q.defer();

            UserImage.get({userId: user.Id}, function(image) {
                delay.resolve(image);
            }, function() {
                delay.reject();
            });

            return delay.promise;
        };
    }]);
});
