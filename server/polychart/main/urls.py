"""
Define the URL endpoints for the Dashboard Builder app. The URL pattern is defined
in the first argument of the `url` function, and the corresponding handler function
is defined as the second argument. Functions will be found in the `views/` directory.
"""
from django.conf.urls import patterns, url

urlpatterns = patterns('polychart.main.views',
  # Account
  url(r'^$'                                       , 'account.accountLogin'         ),# overridden by site
  url(r'^forgot-password$'                        , 'account.accountForgotPassword'),
  url(r'^login$'                                  , 'account.accountLogin'         ),
  url(r'^logout$'                                 , 'account.accountLogout'        ),
  url(r'^reset-password$'                         , 'account.accountResetPassword' ),
  url(r'^settings$'                               , 'user.userSettings'            ),
  url(r'^signup$'                                 , 'account.accountSignup'        ),

  # DBB pages
  url(r'^home$'                                   , 'home.show'                    ),
  url(r'^demo$'                                   , 'demo.demoShow'                ),
  url(r'^dashboard/([^/]+)/([^/]+)$'              , 'dashboard.dashShow'           ),

  # DBB AJAX endpoints
  url(r'^api/dashboard/([^/]+)/delete$'           , 'dashboard.dashDelete'         ),
  url(r'^api/dashboard/([^/]+)/update$'           , 'dashboard.dashUpdate'         ),
  url(r'^api/dashboard/create$'                   , 'dashboard.dashCreate'         ),
  url(r'^api/dashboard/export/code$'              , 'export.dashExportCode'        ),
  url(r'^api/dashboard/export/(.+)'               , 'export.dashExport'            ),
  url(r'^api/dashboard/list$'                     , 'dashboard.dashList'           ),
  url(r'^api/data-source/([^/]+)/delete$'         , 'dataSource.dsDelete'          ),
  url(r'^api/data-source/([^/]+)/tables/list$'    , 'dataSource.tableList'         ),
  url(r'^api/data-source/([^/]+)/tables/meta$'    , 'dataSource.tableMeta'         ),
  url(r'^api/data-source/([^/]+)/tables/query$'   , 'dataSource.tableQuery'        ),
  url(r'^api/data-source/callback$'               , 'dataSource.dsCallback'        ),
  url(r'^api/data-source/create$'                 , 'dataSource.dsCreate'          ),
  url(r'^api/data-source/list$'                   , 'dataSource.dsList'            ),
  url(r'^api/ssh/file-exists$'                    , 'ssh.sshFileExists'            ),
  url(r'^api/ssh/keygen$'                         , 'ssh.sshKeygen'                ),
  url(r'^api/tutorial/mark-complete$'             , 'tutorial.tutorialComplete'    ),

  # DBB CSV uploads
  url(r'^api/upload/get-key$'                     , 'upload.getKey'                ),
  url(r'^api/upload/upload-file/([^/]+)/([0-9]+)$', 'upload.postFile'              ),
  url(r'^api/upload/preview/csv/([^/]+)/([0-9]+)$', 'upload.previewCsv'            ),
  url(r'^api/upload/clean/csv/([^/]+)$'           , 'upload.cleanCsv'              ),

  # DBB connection script
  url(r'^api/pending-data-source/create$'         , 'dataSource.dsPendingCreate'   ),
  url(r'^pending-data-source/([^/]+)/verify$'     , 'dataSource.dsPendingVerify'   ),
  url(r'^api/pending-data-source/([^/]+)/delete$' , 'dataSource.dsPendingDelete'   ))
