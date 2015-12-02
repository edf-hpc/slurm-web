/*
 * Copyright (C) 2015 EDF SA
 *
 * This file is part of slurm-web.
 *
 * slurm-web is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * slurm-web is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with slurm-web.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

require.config({
  paths: {
    text: '/javascript/requirejs/text.min',
    jquery: '/javascript/jquery/jquery.min',
    'jquery-tablesorter': '/javascript/jquery-tablesorter/jquery.tablesorter.min',
    'jquery-flot': '/javascript/jquery-flot/jquery.flot.min',
    'jquery-flot-pie': '/javascript/jquery-flot/jquery.flot.pie.min',
    xdomain: '../../js/libraries/xdomain.min',
    handlebars: '/javascript/handlebars/handlebars',
    bootstrap: '/javascript/bootstrap/js/bootstrap',
    'bootstrap-typeahead': '/javascript/bootstrap/js/typeahead.jquery',
    'bootstrap-tagsinput': '/javascript/bootstrap/js/bootstrap-tagsinput.min',
    d3: '/javascript/d3/d3.min',
    'cluster-utils': '../../js/utils/cluster',
    'token-utils': '../../js/utils/token',
    'user-utils': '../../js/utils/user',
    'date-utils': '../../js/utils/date',
    'tablesorter-utils': '../../js/utils/tablesorter',
    'jobs-utils': '../../js/utils/jobs',
    'nodes-utils': '../../js/utils/node',
    'page-utils': '../../js/utils/page',
    'ajax-utils': '../../js/utils/ajax',
    'flot-utils': '../../js/utils/flot',
    'tagsinput-utils': '../../js/utils/tagsinput',
    'string-helpers': '../../js/helpers/string',
    'array-helpers': '../../js/helpers/array',
    'jobs-helpers': '../../js/helpers/jobs',
    'number-helpers': '../../js/helpers/number',
    'boolean-helpers': '../../js/helpers/boolean',
    'date-helpers': '../../js/helpers/date',
    'different-helpers': '../../js/helpers/different',
    'keycode-helpers': '../../js/helpers/keycode',
    '2d-draw': '../../js/draw/2d-draw',
    'colors-draw': '../../js/draw/colors',
    '2d-intersections-draw': '../../js/draw/2d-intersections',
    '2d-legend-draw': '../../js/draw/2d-legend',
    'factor-draw': '../../js/draw/factor',
    login: '../../js/core/login/login',
    navbar: '../../js/core/navbar/navbar',
    clusters: '../../js/core/clusters/clusters',
    jobs: '../../js/modules/jobs/jobs',
    racks: '../../js/modules/racks/racks',
    'jobs-map': '../../js/modules/jobs-map/jobs-map',
    partitions: '../../js/modules/partitions/partitions',
    qos: '../../js/modules/qos/qos',
    reservations: '../../js/modules/reservations/reservations',
    '3d-view': '../../js/modules/3d-view/3d-view',
    gantt: '../../js/modules/gantt/gantt',
    topology: '../../js/modules/topology/topology',
    'topology-utils': '../../js/utils/topology',
    'fake-placeholder': '../../js/utils/fakePlaceholder'
  },
  shim: {
    jquery: {
      exports: '$'
    },
    'jquery-tablesorter': {
      deps: [ 'jquery' ]
    },
    'jquery-flot': {
      deps: [ 'jquery' ]
    },
    'jquery-flot-pie': {
      deps: [ 'jquery', 'jquery-flot' ]
    },
    handlebars: {
      exports: 'Handlebars'
    },
    bootstrap: {
      deps: [ 'jquery' ]
    },
    'bootstrap-typeahead': {
      deps: [ 'jquery' ],
      init: function ($) {
        return require.s.contexts._.registry['typeahead.js'].factory($);
      }
    },
    'bootstrap-tagsinput': {
      deps: [ 'jquery', 'bootstrap', 'bootstrap-typeahead' ]
    }
  }
});

var isIE = false || !!document.documentMode;

if (isIE) {
  require(['xdomain'], function(xdomain){
    var slaves = {};
    for (var index in window.clusters) {
      slaves[window.clusters[index].api.url] = window.clusters[index].api.path + "/proxy";
    }
    xdomain.slaves(slaves);
  })
}

require([
  'page-utils',
  'text!/slurm-web-conf/config.json',
  'token-utils',
  'user-utils',
  'login',
  'navbar',
  'clusters',
  'jobs',
  'racks',
  'jobs-map',
  'qos',
  'partitions',
  'reservations',
  '3d-view',
  'gantt',
  'topology',
  'ajax-utils'
], function (Page, config, token, user, Login, Navbar, Clusters, Jobs, Racks, JobsMap, QOS, Partitions, Reservations, d3View, Gantt, Topology) {
  config = JSON.parse(config);
  var clusters = new Clusters(config);
  clusters.init();
  var firstLoad = true;
  var page = new Page();

  $(document).on('loadPage', function(e, options) {
    e.stopPropagation();
    $(document).trigger('destroyNavbar');

    var navbar = new Navbar(options.config);
    navbar.init();

    $('title').html(options.config.cluster.name + '\'s HPC Dashboard');

    $(document).trigger('show', { page: options.config.STARTPAGE });
  })

  $(document).on('logout', function (e) {
    e.preventDefault();

    $(document).trigger('show', { page: config.cluster.authentication.enabled ? 'login' : config.STARTPAGE });
  });

  $(document).on('show', function (e, options) {
    e.stopPropagation();

    page.destroy(true);
    page = new Page();
    $('#flash').hide();

    switch (options.page) {
    case 'login':
      page = new Login(config);
      break;
    case 'jobs':
      page = new Jobs(config);
      break;
    case 'jobsmap':
      page = new JobsMap(config);
      break;
    case 'partitions':
      page = new Partitions(config);
      break;
    case 'qos':
      page = new QOS(config);
      break;
    case 'racks':
      page = new Racks(config);
      break;
    case 'reservations':
      page = new Reservations(config);
      break;
    case '3dview':
      page = new d3View(config);
      break;
    case 'gantt':
      page = new Gantt(config);
      break;
    case 'topology':
      page = new Topology(config);
      break;
    }

    if (page.hasOwnProperty('init')) {
      page.init();
    }

    if (page.hasOwnProperty('refresh')) {
      page.refresh();
    }
  });

  $(document).trigger('loadPage', { config: config });

  $(window).resize(function() {
    $('body>.container-fluid').css({'margin-top': $('nav').height()+'px'});
  });
});
