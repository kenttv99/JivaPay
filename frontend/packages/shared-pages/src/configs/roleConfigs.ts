// Конфигурации для административных ролей (admin, teamlead, support)
export const DASHBOARD_CONFIGS = {
  admin: {
    permissions: {
      viewMetrics: 'dashboard:view:*',
      viewOrders: 'orders:view:*',
      viewUsers: 'users:view:*',
      viewStores: 'stores:view:*',
      viewRequisites: 'requisites:view:*',
      viewFinance: 'finance:view:*'
    },
    config: { 
      showAdvancedMetrics: true, 
      enableExport: true,
      showAllOrderTypes: true,
      showPlatformBalances: true,
      enableUserManagement: true,
      enableStoreManagement: true,
      enableRequisiteModeration: true
    }
  },
  
  teamlead: {
    permissions: {
      viewMetrics: 'dashboard:view:team',
      viewOrders: 'orders:view:team',
      viewUsers: 'users:view:team',
      viewRequisites: 'requisites:view:team'
    },
    config: { 
      showAdvancedMetrics: true, 
      enableExport: false,
      showAllOrderTypes: true,
      showPlatformBalances: false,
      enableUserManagement: false,
      enableStoreManagement: false,
      enableRequisiteModeration: true
    }
  },
  
  support: {
    permissions: {
      viewMetrics: 'dashboard:view:basic',
      viewOrders: 'orders:view:assigned',
      viewUsers: 'users:view:assigned'
    },
    config: { 
      showAdvancedMetrics: false, 
      enableExport: false,
      showAllOrderTypes: false,
      showPlatformBalances: false,
      enableUserManagement: false,
      enableStoreManagement: false,
      enableRequisiteModeration: false
    }
  }
} as const;

export const ORDERS_CONFIGS = {
  admin: {
    permissions: {
      viewAll: 'orders:view:*',
      editAny: 'orders:edit:*',
      viewDetails: 'orders:details:*',
      exportData: 'orders:export:*'
    },
    filters: {
      showAllTypes: true,      // PayIn + PayOut
      showAllStatuses: true,   // все статусы ордеров
      showAllUsers: true,      // все пользователи
      showTraderInfo: true,    // информация о трейдерах
      showStoreInfo: true,     // информация о магазинах
      showCommissions: true    // комиссии платформы
    }
  },
  
  teamlead: {
    permissions: {
      viewTeam: 'orders:view:team',
      editTeam: 'orders:edit:team',
      viewDetails: 'orders:details:team'
    },
    filters: {
      showAllTypes: true,      // PayIn + PayOut для команды
      showAllStatuses: true,   // все статусы
      showAllUsers: false,     // только команда
      showTraderInfo: true,    // информация о трейдерах команды
      showStoreInfo: false,    // нет доступа к магазинам
      showCommissions: false   // нет доступа к комиссиям платформы
    }
  },
  
  support: {
    permissions: {
      viewAssigned: 'orders:view:assigned',
      editAssigned: 'orders:edit:assigned'
    },
    filters: {
      showAllTypes: false,     // только проблемные ордера
      showAllStatuses: false,  // только disputed, failed, требующие поддержки
      showAllUsers: false,     // только назначенные
      showTraderInfo: false,   // базовая информация
      showStoreInfo: false,    // базовая информация
      showCommissions: false   // нет доступа к комиссиям
    }
  }
} as const;

export const USERS_CONFIGS = {
  admin: {
    permissions: {
      viewAll: 'users:view:*',
      editAny: 'users:edit:*',
      createAny: 'users:create:*',
      deleteAny: 'users:delete:*'
    },
    config: {
      showAllRoles: true,      // админы, трейдеры, мерчанты, саппорт, тимлиды
      enableRoleManagement: true,
      enablePermissionManagement: true,
      showSensitiveData: true
    }
  },
  
  teamlead: {
    permissions: {
      viewTeam: 'users:view:team',
      editTeam: 'users:edit:team'
    },
    config: {
      showAllRoles: false,     // только трейдеры команды
      enableRoleManagement: false,
      enablePermissionManagement: false,
      showSensitiveData: false
    }
  },
  
  support: {
    permissions: {
      viewAssigned: 'users:view:assigned',
      editBasic: 'users:edit:basic'
    },
    config: {
      showAllRoles: false,     // только назначенные пользователи
      enableRoleManagement: false,
      enablePermissionManagement: false,
      showSensitiveData: false
    }
  }
} as const;

export const FINANCE_CONFIGS = {
  admin: {
    permissions: {
      viewPlatform: 'finance:view:platform',
      viewBalances: 'balances:view:*',
      viewCommissions: 'commissions:view:*',
      exportData: 'finance:export:*'
    },
    config: {
      showPlatformBalances: true,
      showAllBalances: true,    // балансы всех пользователей
      showCommissionBreakdown: true,
      enableFinancialReports: true,
      showBalanceCharts: true,
      showVolumeAnalytics: true,
      showCommissionAnalytics: true,
      showPlatformRevenue: true,
      showSensitiveData: true,
      enableExport: true
    }
  },
  
  teamlead: {
    permissions: {
      viewTeam: 'finance:view:team',
      viewBalances: 'balances:view:team'
    },
    config: {
      showPlatformBalances: false,
      showAllBalances: false,   // только команда
      showCommissionBreakdown: false,
      enableFinancialReports: false,
      showBalanceCharts: true,
      showVolumeAnalytics: true,
      showCommissionAnalytics: false,
      showPlatformRevenue: false,
      showSensitiveData: false,
      enableExport: false
    }
  },
  
  support: {
    permissions: {
      viewBasic: 'finance:view:basic'
    },
    config: {
      showPlatformBalances: false,
      showAllBalances: false,   // только для поддержки пользователей
      showCommissionBreakdown: false,
      enableFinancialReports: false,
      showBalanceCharts: false,
      showVolumeAnalytics: false,
      showCommissionAnalytics: false,
      showPlatformRevenue: false,
      showSensitiveData: false,
      enableExport: false
    }
  }
} as const;

// Типы для конфигураций
export type UserRole = 'admin' | 'teamlead' | 'support';
export type DashboardConfig = typeof DASHBOARD_CONFIGS[UserRole];
export type OrdersConfig = typeof ORDERS_CONFIGS[UserRole];
export type UsersConfig = typeof USERS_CONFIGS[UserRole];
export type FinanceConfig = typeof FINANCE_CONFIGS[UserRole]; 