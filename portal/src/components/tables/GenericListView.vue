<template>
  <div class="space-y-4">
    <!-- PAGE HEADER -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 border border-slate-200 rounded-xl shadow-2xs">
      <div>
        <div class="flex items-center space-x-2">
          <h1 class="text-xl font-bold text-slate-900 tracking-tight">{{ computedTitle }}</h1>
          <span v-if="meta?.is_tree" class="px-2 py-0.5 text-xs font-semibold bg-indigo-50 text-indigo-700 rounded border border-indigo-200">
            Tree DocType
          </span>
          <span v-if="meta?.is_submittable" class="px-2 py-0.5 text-xs font-semibold bg-emerald-50 text-emerald-700 rounded border border-emerald-200">
            Submittable
          </span>
        </div>
        <p class="text-xs text-slate-500 mt-1 font-sans">{{ computedDescription }}</p>
      </div>

      <div class="flex items-center space-x-2">
        <!-- Tree View Toggle -->
        <button
          v-if="meta?.is_tree"
          @click="toggleViewMode"
          class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-medium flex items-center space-x-1.5 transition-colors border border-slate-300"
        >
          <Layers class="w-3.5 h-3.5" />
          <span>{{ viewMode === 'tree' ? 'List View' : 'Tree View' }}</span>
        </button>

        <!-- Refresh Button -->
        <button
          @click="loadData"
          class="px-3 py-1.5 bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 rounded text-xs font-medium flex items-center space-x-1.5 transition-colors shadow-2xs"
          title="Refresh List"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" />
          <span>Refresh</span>
        </button>

        <!-- New Document Button -->
        <button
          v-if="canCreate"
          @click="openCreateForm"
          class="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-xs"
        >
          <Plus class="w-4 h-4" />
          <span>New {{ meta?.label || docType }}</span>
        </button>
      </div>
    </div>

    <!-- SINGLE DOCTYPE WARNING CARD -->
    <div v-if="meta?.issingle" class="bg-amber-50 border border-amber-200 rounded-xl p-6 text-center space-y-3">
      <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-amber-100 text-amber-600">
        <FileText class="w-6 h-6" />
      </div>
      <h3 class="text-base font-semibold text-amber-900">{{ meta.label || docType }} is a Single DocType</h3>
      <p class="text-xs text-amber-700 max-w-md mx-auto">
        Single DocTypes store a single global document/settings record rather than a list of multiple rows.
      </p>
      <button
        @click="openDocument(meta.name, meta.name)"
        class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs rounded-lg transition-colors"
      >
        Open {{ meta.label || docType }} Settings
      </button>
    </div>

    <!-- CHILD TABLE WARNING CARD -->
    <div v-else-if="meta?.istable" class="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center space-y-2">
      <div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-slate-200 text-slate-600">
        <Layers class="w-5 h-5" />
      </div>
      <h3 class="text-sm font-semibold text-slate-800">{{ meta.label || docType }} is a Child Table</h3>
      <p class="text-xs text-slate-500 max-w-md mx-auto">
        Child tables are embedded sub-records managed inside parent forms and do not have standalone list views.
      </p>
    </div>

    <!-- MAIN LIST CONTENT -->
    <template v-else>
      <!-- TOOLBAR & FILTERS -->
      <div class="bg-white border border-slate-200 rounded-xl p-3.5 shadow-2xs space-y-3">
        <div class="flex flex-wrap items-center justify-between gap-2.5">
          <!-- Search Input -->
          <div class="relative flex-1 min-w-[220px] max-w-sm">
            <Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              v-model="searchText"
              @input="onSearchInput"
              type="text"
              :placeholder="`Search ${meta?.label || docType}...`"
              class="w-full bg-white border border-slate-200 rounded-lg pl-9 pr-8 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-sans"
            />
            <button
              v-if="searchText"
              @click="clearSearch"
              class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5"
            >
              <X class="w-3.5 h-3.5" />
            </button>
          </div>

          <!-- Controls Group -->
          <div class="flex items-center space-x-2 flex-wrap gap-y-1.5">
            <!-- Filter Drawer Toggle Button -->
            <button
              @click="toggleFilterModal"
              class="px-3 py-1.5 rounded text-xs font-medium flex items-center space-x-1.5 transition-colors border"
              :class="activeFilters.length > 0 ? 'bg-blue-50 border-blue-200 text-blue-700 font-semibold' : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-700'"
            >
              <Filter class="w-3.5 h-3.5" />
              <span>Filter</span>
              <span v-if="activeFilters.length > 0" class="ml-1 px-1.5 py-0.2 bg-blue-600 text-white text-[10px] font-mono rounded-full font-bold">
                {{ activeFilters.length }}
              </span>
            </button>

            <!-- Sort Popover Toggle -->
            <div class="relative">
              <button
                @click="showSortPopover = !showSortPopover"
                class="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded text-xs font-medium flex items-center space-x-1.5 transition-colors"
              >
                <ArrowUpDown class="w-3.5 h-3.5" />
                <span>Sort: {{ getSortLabel(sortField) }} ({{ sortOrder.toUpperCase() }})</span>
                <ChevronDown class="w-3.5 h-3.5 text-slate-400" />
              </button>

              <!-- Sort Dropdown Menu -->
              <div
                v-if="showSortPopover"
                class="absolute right-0 mt-1 w-56 bg-white border border-slate-200 rounded-lg shadow-lg z-30 p-2 text-xs space-y-2 animate-fade-in"
              >
                <div class="font-semibold text-slate-500 uppercase text-[10px] px-2 py-1">Sort Field</div>
                <div class="max-h-48 overflow-y-auto space-y-0.5">
                  <button
                    v-for="col in availableSortColumns"
                    :key="col.fieldname"
                    @click="applySortField(col.fieldname)"
                    class="w-full text-left px-2 py-1.5 rounded hover:bg-slate-100 flex items-center justify-between"
                    :class="{ 'bg-blue-50 text-blue-700 font-semibold': sortField === col.fieldname }"
                  >
                    <span>{{ col.label }}</span>
                    <Check v-if="sortField === col.fieldname" class="w-3.5 h-3.5 text-blue-600" />
                  </button>
                </div>
                <div class="border-t border-slate-200 pt-2 flex items-center justify-between px-2">
                  <span class="text-slate-500 font-medium">Order:</span>
                  <div class="flex items-center space-x-1">
                    <button
                      @click="applySortOrder('asc')"
                      class="px-2 py-0.5 rounded text-[11px] font-mono border"
                      :class="sortOrder === 'asc' ? 'bg-blue-600 text-white border-blue-600 font-bold' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
                    >
                      ASC
                    </button>
                    <button
                      @click="applySortOrder('desc')"
                      class="px-2 py-0.5 rounded text-[11px] font-mono border"
                      :class="sortOrder === 'desc' ? 'bg-blue-600 text-white border-blue-600 font-bold' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
                    >
                      DESC
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Columns Popover Toggle -->
            <div class="relative">
              <button
                @click="showColumnPopover = !showColumnPopover"
                class="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded text-xs font-medium flex items-center space-x-1.5 transition-colors"
              >
                <Columns class="w-3.5 h-3.5" />
                <span>Columns</span>
              </button>

              <!-- Columns Dropdown Menu -->
              <div
                v-if="showColumnPopover"
                class="absolute right-0 mt-1 w-60 bg-white border border-slate-200 rounded-lg shadow-lg z-30 p-2.5 text-xs space-y-2"
              >
                <div class="flex items-center justify-between font-semibold text-slate-500 uppercase text-[10px]">
                  <span>Customize Columns</span>
                  <button @click="resetColumns" class="text-blue-600 hover:underline">Reset</button>
                </div>
                <div class="max-h-60 overflow-y-auto space-y-1.5 pr-1">
                  <label
                    v-for="col in allAvailableColumns"
                    :key="col.key"
                    class="flex items-center space-x-2 px-1 py-0.5 hover:bg-slate-50 rounded cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      :checked="isColumnVisible(col.key)"
                      @change="toggleColumnVisibility(col.key)"
                      class="rounded text-blue-600 focus:ring-blue-500 w-3.5 h-3.5"
                    />
                    <span class="text-slate-700 truncate">{{ col.label }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Export Button -->
            <button
              @click="exportToCSV"
              class="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded text-xs font-medium flex items-center space-x-1.5 transition-colors"
              title="Export filtered records to CSV"
            >
              <Download class="w-3.5 h-3.5" />
              <span class="hidden sm:inline">Export</span>
            </button>
          </div>
        </div>

        <!-- ACTIVE FILTER CHIPS BAR -->
        <div v-if="activeFilters.length > 0" class="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100">
          <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mr-1">Active Filters:</span>
          <div
            v-for="(filter, idx) in activeFilters"
            :key="idx"
            class="inline-flex items-center space-x-1 px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-full text-xs font-medium"
          >
            <span>{{ filter.label }}</span>
            <span class="font-mono text-blue-500 font-bold">{{ filter.operator }}</span>
            <span class="font-mono font-semibold">{{ formatFilterValue(filter) }}</span>
            <button @click="removeFilter(idx)" class="ml-1 hover:bg-blue-200 rounded-full p-0.5 text-blue-600">
              <X class="w-3 h-3" />
            </button>
          </div>
          <button
            @click="clearAllFilters"
            class="text-xs font-semibold text-rose-600 hover:text-rose-700 hover:underline px-2 py-0.5 transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>

      <!-- FILTER EDITOR DRAWER / MODAL -->
      <div
        v-if="showFilterModal"
        class="fixed inset-0 bg-slate-900/30 backdrop-blur-2xs flex justify-end z-50 animate-fade-in"
        @click.self="showFilterModal = false"
      >
        <div class="w-full max-w-lg bg-white h-full flex flex-col shadow-2xl border-l border-slate-200">
          <!-- Drawer Header -->
          <div class="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <div>
              <h3 class="text-base font-bold text-slate-900 flex items-center space-x-2">
                <Filter class="w-4 h-4 text-blue-600" />
                <span>Filter {{ meta?.label || docType }}</span>
              </h3>
              <p class="text-xs text-slate-500 mt-0.5">Build exact metadata-driven filter conditions</p>
            </div>
            <button @click="showFilterModal = false" class="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/50">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Filter Form Body -->
          <div class="flex-1 overflow-y-auto p-5 space-y-6">
            <!-- Standard Quick Filters -->
            <div v-if="meta?.standard_filters && meta.standard_filters.length > 0" class="space-y-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Standard Filters</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div v-for="sf in meta.standard_filters" :key="sf.fieldname" class="space-y-1">
                  <label class="text-xs font-semibold text-slate-600">{{ sf.label }}</label>

                  <!-- Link Standard Filter -->
                  <div v-if="sf.fieldtype === 'Link'">
                    <LinkSelector
                      :doctype="sf.options"
                      :model-value="getStandardFilterValue(sf.fieldname)"
                      @update:model-value="val => setStandardFilter(sf, '=', val)"
                    />
                  </div>

                  <!-- Select Standard Filter -->
                  <select
                    v-else-if="sf.fieldtype === 'Select'"
                    :value="getStandardFilterValue(sf.fieldname)"
                    @change="e => setStandardFilter(sf, '=', e.target.value)"
                    class="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-blue-500 font-sans"
                  >
                    <option value="">All {{ sf.label }}s</option>
                    <option v-for="opt in parseSelectOptions(sf.options)" :key="opt" :value="opt">{{ opt }}</option>
                  </select>

                  <!-- Generic Text/Data Standard Filter -->
                  <input
                    v-else
                    :value="getStandardFilterValue(sf.fieldname)"
                    @change="e => setStandardFilter(sf, 'like', e.target.value)"
                    type="text"
                    :placeholder="`Filter by ${sf.label}...`"
                    class="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-blue-500 font-sans"
                  />
                </div>
              </div>
            </div>

            <!-- Custom Advanced Filters Builder -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Custom Filter Conditions</h4>
                <button
                  @click="addFilterCondition"
                  class="px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded text-xs font-semibold flex items-center space-x-1 transition-colors"
                >
                  <Plus class="w-3.5 h-3.5" />
                  <span>Add Condition</span>
                </button>
              </div>

              <div v-if="draftFilters.length === 0" class="text-center py-6 border-2 border-dashed border-slate-200 rounded-xl">
                <p class="text-xs text-slate-400">No custom filter conditions added yet.</p>
              </div>

              <div v-else class="space-y-3">
                <div
                  v-for="(f, index) in draftFilters"
                  :key="index"
                  class="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-2.5"
                >
                  <div class="flex items-center justify-between">
                    <span class="text-[10px] font-mono font-bold text-slate-400 uppercase">Condition #{{ index + 1 }}</span>
                    <button @click="removeDraftFilter(index)" class="text-slate-400 hover:text-rose-600 p-0.5">
                      <X class="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <!-- Field Picker -->
                    <div>
                      <label class="text-[10px] font-semibold text-slate-500 uppercase">Field</label>
                      <select
                        v-model="f.fieldname"
                        @change="onDraftFieldChange(f)"
                        class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:border-blue-500 font-sans"
                      >
                        <option v-for="field in allFilterableFields" :key="field.fieldname" :value="field.fieldname">
                          {{ field.label }}
                        </option>
                      </select>
                    </div>

                    <!-- Operator Picker -->
                    <div>
                      <label class="text-[10px] font-semibold text-slate-500 uppercase">Operator</label>
                      <select
                        v-model="f.operator"
                        class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:border-blue-500 font-mono"
                      >
                        <option v-for="op in getAvailableOperators(f.fieldtype)" :key="op.value" :value="op.value">
                          {{ op.label }}
                        </option>
                      </select>
                    </div>

                    <!-- Value Input (Type-Aware) -->
                    <div>
                      <label class="text-[10px] font-semibold text-slate-500 uppercase">Value</label>

                      <!-- Select Field Value -->
                      <select
                        v-if="f.fieldtype === 'Select'"
                        v-model="f.value"
                        class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:border-blue-500 font-sans"
                      >
                        <option value="">Select option...</option>
                        <option v-for="opt in parseSelectOptions(f.options)" :key="opt" :value="opt">{{ opt }}</option>
                      </select>

                      <!-- Check Field Value -->
                      <select
                        v-else-if="f.fieldtype === 'Check'"
                        v-model="f.value"
                        class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:border-blue-500 font-sans"
                      >
                        <option :value="1">Yes (True)</option>
                        <option :value="0">No (False)</option>
                      </select>

                      <!-- Link Search Value -->
                      <div v-else-if="f.fieldtype === 'Link'">
                        <LinkSelector
                          :doctype="f.options"
                          :model-value="f.value"
                          @update:model-value="val => f.value = val"
                        />
                      </div>

                      <!-- Date Value -->
                      <input
                        v-else-if="['Date', 'Datetime'].includes(f.fieldtype)"
                        v-model="f.value"
                        type="date"
                        class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:border-blue-500 font-mono"
                      />

                      <!-- Numeric Value -->
                      <input
                        v-else-if="['Int', 'Float', 'Currency', 'Percent'].includes(f.fieldtype)"
                        v-model.number="f.value"
                        type="number"
                        step="any"
                        placeholder="Value"
                        class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:border-blue-500 font-mono"
                      />

                      <!-- Default Text Value -->
                      <input
                        v-else
                        v-model="f.value"
                        type="text"
                        placeholder="Value..."
                        class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:border-blue-500 font-sans"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Drawer Footer -->
          <div class="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
            <button
              @click="clearDraftFilters"
              class="text-xs font-semibold text-rose-600 hover:text-rose-700 hover:underline px-2 py-1"
            >
              Reset Filters
            </button>

            <div class="flex items-center space-x-2">
              <button
                @click="showFilterModal = false"
                class="px-3.5 py-1.5 bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-medium rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                @click="applyDraftFilters"
                class="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors shadow-xs"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- BULK SELECTION ACTIONS TOOLBAR -->
      <div
        v-if="selectedRowNames.length > 0"
        class="bg-indigo-900 text-white px-4 py-2.5 rounded-xl shadow-md flex items-center justify-between text-xs font-medium animate-slide-down"
      >
        <div class="flex items-center space-x-3">
          <span class="font-mono font-bold px-2 py-0.5 bg-indigo-800 text-indigo-200 rounded-md">
            {{ selectedRowNames.length }} Selected
          </span>
          <span>Perform bulk operation on selected documents</span>
        </div>

        <div class="flex items-center space-x-2">
          <button
            v-if="canDelete"
            @click="performBulkDelete"
            class="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded font-semibold flex items-center space-x-1 transition-colors"
          >
            <Trash2 class="w-3.5 h-3.5" />
            <span>Delete Selected</span>
          </button>

          <button
            @click="clearSelection"
            class="px-2.5 py-1 bg-indigo-800 hover:bg-indigo-700 text-indigo-200 rounded transition-colors"
          >
            Deselect All
          </button>
        </div>
      </div>

      <!-- TREE VIEW COMPONENT MODE -->
      <div v-if="viewMode === 'tree'" class="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
        <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-4 flex items-center space-x-2">
          <Layers class="w-4 h-4 text-indigo-600" />
          <span>{{ meta?.label || docType }} Tree Hierarchy</span>
        </h4>
        <TreeHierarchyView :doctype="docType" @node-click="handleRowClick" />
      </div>

      <!-- TABLE VIEW MODE -->
      <div v-else class="bg-white border border-slate-200 rounded-xl shadow-2xs overflow-hidden">
        <!-- Loading State -->
        <LoadingState v-if="loading" message="Loading records..." />

        <!-- Error State -->
        <ErrorState v-else-if="error" :message="error" @retry="loadData" />

        <!-- Empty State -->
        <div v-else-if="rows.length === 0" class="py-12 px-4 text-center space-y-3">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 text-slate-400">
            <Search class="w-6 h-6" />
          </div>
          <h4 class="text-sm font-bold text-slate-800">No {{ meta?.label || docType }} records found</h4>
          <p class="text-xs text-slate-500 max-w-sm mx-auto">
            {{ activeFilters.length > 0 || searchText ? 'No records match your active search or filter criteria.' : 'There are currently no records created for this document type.' }}
          </p>
          <div class="flex items-center justify-center space-x-2 pt-2">
            <button
              v-if="activeFilters.length > 0 || searchText"
              @click="clearAllFilters"
              class="px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold text-xs rounded-lg transition-colors"
            >
              Clear Search & Filters
            </button>
            <button
              v-if="canCreate"
              @click="openCreateForm"
              class="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg transition-colors shadow-xs"
            >
              Create New Record
            </button>
          </div>
        </div>

        <!-- Data Table Grid -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs font-sans">
            <thead class="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider select-none">
              <tr>
                <!-- Select All Checkbox -->
                <th class="py-2.5 px-3 w-10 text-center">
                  <input
                    type="checkbox"
                    :checked="isAllSelected"
                    @change="toggleSelectAll"
                    class="rounded text-blue-600 focus:ring-blue-500 w-3.5 h-3.5"
                  />
                </th>

                <!-- Dynamic Column Headers -->
                <th
                  v-for="col in activeColumns"
                  :key="col.key"
                  @click="applySortField(col.key)"
                  class="py-2.5 px-3 cursor-pointer hover:bg-slate-100/80 transition-colors group"
                >
                  <div class="flex items-center space-x-1">
                    <span>{{ col.label }}</span>
                    <ArrowUpDown v-if="sortField !== col.key" class="w-3 h-3 text-slate-300 opacity-0 group-hover:opacity-100" />
                    <span v-else class="text-blue-600 font-bold font-mono text-[11px]">
                      {{ sortOrder === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>

                <!-- Row Actions Header -->
                <th class="py-2.5 px-3 w-16 text-right">Actions</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-200/60">
              <tr
                v-for="row in rows"
                :key="row.name"
                class="hover:bg-slate-50/80 transition-colors group"
                :class="{ 'bg-blue-50/40': selectedRowNames.includes(row.name) }"
              >
                <!-- Row Selection Checkbox -->
                <td class="py-2.5 px-3 text-center" @click.stop>
                  <input
                    type="checkbox"
                    :checked="selectedRowNames.includes(row.name)"
                    @change="toggleRowSelect(row.name)"
                    class="rounded text-blue-600 focus:ring-blue-500 w-3.5 h-3.5"
                  />
                </td>

                <!-- Cells -->
                <td
                  v-for="col in activeColumns"
                  :key="col.key"
                  @click="handleRowClick(row)"
                  class="py-2.5 px-3 text-slate-700 font-medium truncate max-w-xs cursor-pointer"
                >
                  <!-- Status Column Badge -->
                  <template v-if="isStatusColumn(col.key)">
                    <StatusBadge :status="row[col.key] || row.status || 'Draft'" />
                  </template>

                  <!-- Link / ID Primary Column -->
                  <template v-else-if="col.key === 'name' || col.key === meta?.title_field">
                    <span class="font-mono text-blue-600 font-bold group-hover:underline">
                      {{ row[col.key] || '—' }}
                    </span>
                  </template>

                  <!-- Checkbox Column -->
                  <template v-else-if="col.fieldtype === 'Check'">
                    <span v-if="row[col.key]" class="text-emerald-600 font-bold">✓ Yes</span>
                    <span v-else class="text-slate-400">—</span>
                  </template>

                  <!-- Formatted Value -->
                  <template v-else>
                    {{ formatCellValue(row[col.key], col.fieldtype) }}
                  </template>
                </td>

                <!-- Row Action Button Menu -->
                <td class="py-2.5 px-3 text-right" @click.stop>
                  <div class="flex items-center justify-end space-x-1">
                    <button
                      @click="handleRowClick(row)"
                      class="p-1 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="View Record"
                    >
                      <Eye class="w-3.5 h-3.5" />
                    </button>
                    <button
                      v-if="canDelete"
                      @click="confirmDeleteRow(row)"
                      class="p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded transition-colors"
                      title="Delete Record"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- SERVER-SIDE PAGINATION FOOTER -->
        <div v-if="totalCount > 0" class="p-3 border-t border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600">
          <div class="flex items-center space-x-3">
            <span>Showing <strong class="font-mono text-slate-900">{{ paginationStart }}</strong> to <strong class="font-mono text-slate-900">{{ paginationEnd }}</strong> of <strong class="font-mono text-slate-900">{{ totalCount }}</strong> records</span>
            
            <div class="flex items-center space-x-1">
              <span class="text-slate-400">|</span>
              <span class="text-slate-500">Page length:</span>
              <select
                :value="pageSize"
                @change="onPageSizeChange"
                class="bg-white border border-slate-200 rounded px-1.5 py-0.5 text-xs text-slate-700 font-mono focus:border-blue-500"
              >
                <option :value="20">20</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
            </div>
          </div>

          <div class="flex items-center space-x-1.5">
            <button
              @click="goToPage(page - 1)"
              :disabled="page <= 1"
              class="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 disabled:opacity-40 disabled:hover:bg-white rounded border border-slate-200 transition-colors font-medium"
            >
              Previous
            </button>
            <span class="px-2 font-mono text-slate-800 font-bold">{{ page }} / {{ maxPage }}</span>
            <button
              @click="goToPage(page + 1)"
              :disabled="page >= maxPage"
              class="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 disabled:opacity-40 disabled:hover:bg-white rounded border border-slate-200 transition-colors font-medium"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search, Plus, RefreshCw, Filter, ArrowUpDown, ChevronDown, Columns,
  Download, X, Trash2, Edit3, Eye, Check, FileText, Layers
} from 'lucide-vue-next'
import LoadingState from '../ui/LoadingState.vue'
import ErrorState from '../ui/ErrorState.vue'
import StatusBadge from './StatusBadge.vue'
import LinkSelector from '../forms/LinkSelector.vue'
import TreeHierarchyView from './TreeHierarchyView.vue'
import {
  getDocTypeMeta, getDocumentList, deleteDocument, deleteDocumentsBulk, searchLinkOptions
} from '../../services/api'
import { useNotificationStore } from '../../stores/notification'
import { extractFrappeErrorMessage } from '../../utils/error'

const props = defineProps({
  docType: { type: String, required: true },
  pageTitle: { type: String, default: '' },
  description: { type: String, default: '' }
})

const emit = defineEmits(['row-click', 'open-create'])

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()

const loading = ref(false)
const error = ref('')
const rows = ref([])
const totalCount = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchText = ref('')

const meta = ref(null)
const viewMode = ref('list')
const sortField = ref('modified')
const sortOrder = ref('desc')

const activeFilters = ref([])
const draftFilters = ref([])
const showFilterModal = ref(false)
const showSortPopover = ref(false)
const showColumnPopover = ref(false)

const userCustomColumns = ref(null)
const selectedRowNames = ref([])

const computedTitle = computed(() => {
  if (props.pageTitle) return props.pageTitle
  if (meta.value?.label) return meta.value.label
  return props.docType
})

const computedDescription = computed(() => {
  if (props.description) return props.description
  return `View and manage ${computedTitle.value} records.`
})

const canCreate = computed(() => {
  if (!meta.value) return true
  if (meta.value.issingle || meta.value.istable) return false
  return meta.value.permissions ? meta.value.permissions.create : true
})

const canDelete = computed(() => {
  if (!meta.value) return true
  return meta.value.permissions ? meta.value.permissions.delete : true
})

const maxPage = computed(() => Math.ceil(totalCount.value / pageSize.value) || 1)
const paginationStart = computed(() => totalCount.value === 0 ? 0 : ((page.value - 1) * pageSize.value) + 1)
const paginationEnd = computed(() => Math.min(page.value * pageSize.value, totalCount.value))

const allFilterableFields = computed(() => {
  if (!meta.value) return []
  const list = []
  
  if (meta.value.system_fields) {
    list.push(...meta.value.system_fields)
  } else {
    list.push(
      { fieldname: 'name', label: 'ID / Name', fieldtype: 'Data' },
      { fieldname: 'modified', label: 'Last Modified', fieldtype: 'Datetime' },
      { fieldname: 'creation', label: 'Creation Date', fieldtype: 'Datetime' }
    )
  }

  if (meta.value.fields) {
    for (const f of meta.value.fields) {
      if (f.fieldname && !list.some(item => item.fieldname === f.fieldname)) {
        list.push({
          fieldname: f.fieldname,
          label: f.label || f.fieldname,
          fieldtype: f.fieldtype || 'Data',
          options: f.options
        })
      }
    }
  }

  return list
})

const allAvailableColumns = computed(() => {
  if (!meta.value) return []
  const cols = []
  
  if (meta.value.list_fields && meta.value.list_fields.length > 0) {
    for (const lf of meta.value.list_fields) {
      cols.push({
        key: lf.key,
        label: lf.label,
        fieldtype: lf.fieldtype,
        options: lf.options
      })
    }
  } else {
    cols.push({ key: 'name', label: 'ID / Name', fieldtype: 'Data' })
    if (meta.value.title_field && meta.value.title_field !== 'name') {
      cols.push({ key: meta.value.title_field, label: 'Title', fieldtype: 'Data' })
    }
    if (meta.value.status_field) {
      cols.push({ key: meta.value.status_field, label: 'Status', fieldtype: 'Select' })
    }
    cols.push({ key: 'modified', label: 'Last Modified', fieldtype: 'Datetime' })
  }

  for (const f of allFilterableFields.value) {
    if (!cols.some(c => c.key === f.fieldname)) {
      cols.push({
        key: f.fieldname,
        label: f.label,
        fieldtype: f.fieldtype,
        options: f.options
      })
    }
  }

  return cols
})

const activeColumns = computed(() => {
  if (userCustomColumns.value && userCustomColumns.value.length > 0) {
    return allAvailableColumns.value.filter(col => userCustomColumns.value.includes(col.key))
  }
  if (meta.value?.list_fields && meta.value.list_fields.length > 0) {
    return meta.value.list_fields
  }
  return allAvailableColumns.value.slice(0, 5)
})

const availableSortColumns = computed(() => {
  return allFilterableFields.value
})

const isAllSelected = computed(() => {
  return rows.value.length > 0 && selectedRowNames.value.length === rows.value.length
})

// METHODS
const loadMeta = async () => {
  try {
    const res = await getDocTypeMeta(props.docType)
    if (res.success) {
      meta.value = res.data
      sortField.value = res.data.sort_field || 'modified'
      sortOrder.value = res.data.sort_order || 'desc'
    } else {
      error.value = res.error?.message || 'Failed to load DocType metadata'
    }
  } catch (err) {
    error.value = extractFrappeErrorMessage(null, err)
  }
}

const loadData = async () => {
  if (meta.value?.issingle || meta.value?.istable) return

  loading.value = true
  error.value = ''
  selectedRowNames.value = []

  try {
    const filterObj = buildApiFilterObject()
    const fieldsToRequest = activeColumns.value.map(c => c.key)
    if (!fieldsToRequest.includes('name')) fieldsToRequest.unshift('name')
    if (meta.value?.status_field && !fieldsToRequest.includes(meta.value.status_field)) {
      fieldsToRequest.push(meta.value.status_field)
    }

    const orderBy = `${sortField.value} ${sortOrder.value}`
    const res = await getDocumentList(props.docType, {
      page: page.value,
      pageLength: pageSize.value,
      filters: filterObj,
      searchText: searchText.value,
      fields: fieldsToRequest,
      orderBy
    })

    if (res.success) {
      rows.value = res.data || []
      totalCount.value = res.meta?.total !== undefined ? res.meta.total : rows.value.length
    } else {
      error.value = res.error?.message || 'Failed to load records'
    }
  } catch (err) {
    error.value = extractFrappeErrorMessage(null, err)
  } finally {
    loading.value = false
  }
}

const buildApiFilterObject = () => {
  const result = []
  for (const f of activeFilters.value) {
    if (f.fieldname && f.operator && f.value !== undefined && f.value !== '') {
      result.push([props.docType, f.fieldname, f.operator, f.value])
    }
  }
  return result
}

const onSearchInput = () => {
  page.value = 1
  loadData()
}

const clearSearch = () => {
  searchText.value = ''
  page.value = 1
  loadData()
}

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'tree' ? 'list' : 'tree'
}

const getSortLabel = (fieldname) => {
  const found = allFilterableFields.value.find(f => f.fieldname === fieldname)
  return found ? found.label : fieldname
}

const applySortField = (fieldname) => {
  if (sortField.value === fieldname) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = fieldname
    sortOrder.value = 'desc'
  }
  showSortPopover.value = false
  loadData()
}

const applySortOrder = (order) => {
  sortOrder.value = order
  showSortPopover.value = false
  loadData()
}

// COLUMNS MANAGEMENT
const isColumnVisible = (key) => {
  return activeColumns.value.some(c => c.key === key)
}

const toggleColumnVisibility = (key) => {
  if (!userCustomColumns.value) {
    userCustomColumns.value = activeColumns.value.map(c => c.key)
  }
  if (userCustomColumns.value.includes(key)) {
    if (userCustomColumns.value.length <= 1) return
    userCustomColumns.value = userCustomColumns.value.filter(k => k !== key)
  } else {
    userCustomColumns.value.push(key)
  }
}

const resetColumns = () => {
  userCustomColumns.value = null
}

// FILTER MODAL / DRAWER
const toggleFilterModal = () => {
  draftFilters.value = activeFilters.value.map(f => ({ ...f }))
  showFilterModal.value = !showFilterModal.value
}

const addFilterCondition = () => {
  const firstField = allFilterableFields.value[0] || { fieldname: 'name', fieldtype: 'Data' }
  draftFilters.value.push({
    fieldname: firstField.fieldname,
    label: firstField.label,
    fieldtype: firstField.fieldtype,
    operator: '=',
    value: '',
    options: firstField.options
  })
}

const removeDraftFilter = (index) => {
  draftFilters.value.splice(index, 1)
}

const clearDraftFilters = () => {
  draftFilters.value = []
}

const onDraftFieldChange = (f) => {
  const metaField = allFilterableFields.value.find(item => item.fieldname === f.fieldname)
  if (metaField) {
    f.label = metaField.label
    f.fieldtype = metaField.fieldtype
    f.options = metaField.options
    f.value = ''
    f.operator = '='
  }
}

const getAvailableOperators = (fieldtype) => {
  if (['Int', 'Float', 'Currency', 'Percent'].includes(fieldtype)) {
    return [
      { value: '=', label: '= (Equals)' },
      { value: '!=', label: '!= (Not Equals)' },
      { value: '>', label: '> (Greater Than)' },
      { value: '<', label: '< (Less Than)' },
      { value: '>=', label: '>= (Greater or Equal)' },
      { value: '<=', label: '<= (Less or Equal)' }
    ]
  }
  if (['Date', 'Datetime'].includes(fieldtype)) {
    return [
      { value: '=', label: '= (On Date)' },
      { value: '!=', label: '!= (Not On Date)' },
      { value: '>', label: '> (After)' },
      { value: '<', label: '< (Before)' },
      { value: '>=', label: '>= (On or After)' },
      { value: '<=', label: '<= (On or Before)' }
    ]
  }
  if (fieldtype === 'Select' || fieldtype === 'Link') {
    return [
      { value: '=', label: '= (Equals)' },
      { value: '!=', label: '!= (Not Equals)' },
      { value: 'in', label: 'IN (One of)' }
    ]
  }
  return [
    { value: 'like', label: 'Contains' },
    { value: '=', label: 'Equals' },
    { value: '!=', label: 'Not Equals' },
    { value: 'not like', label: 'Does Not Contain' }
  ]
}

const parseSelectOptions = (optionsStr) => {
  if (!optionsStr) return []
  if (Array.isArray(optionsStr)) return optionsStr
  return String(optionsStr).split('\n').map(s => s.trim()).filter(Boolean)
}

const getStandardFilterValue = (fieldname) => {
  const found = activeFilters.value.find(f => f.fieldname === fieldname)
  return found ? found.value : ''
}

const setStandardFilter = (sf, operator, val) => {
  const existingIdx = activeFilters.value.findIndex(f => f.fieldname === sf.fieldname)
  if (!val && val !== 0) {
    if (existingIdx !== -1) activeFilters.value.splice(existingIdx, 1)
  } else {
    const filterItem = {
      fieldname: sf.fieldname,
      label: sf.label,
      fieldtype: sf.fieldtype,
      operator,
      value: val,
      options: sf.options
    }
    if (existingIdx !== -1) {
      activeFilters.value[existingIdx] = filterItem
    } else {
      activeFilters.value.push(filterItem)
    }
  }
  page.value = 1
  loadData()
}

const applyDraftFilters = () => {
  activeFilters.value = draftFilters.value.filter(f => f.fieldname && f.value !== '' && f.value !== undefined)
  showFilterModal.value = false
  page.value = 1
  loadData()
}

const removeFilter = (idx) => {
  activeFilters.value.splice(idx, 1)
  page.value = 1
  loadData()
}

const clearAllFilters = () => {
  activeFilters.value = []
  searchText.value = ''
  page.value = 1
  loadData()
}

const formatFilterValue = (filter) => {
  if (filter.fieldtype === 'Check') return filter.value ? 'Yes' : 'No'
  return String(filter.value)
}

// CELL FORMATTING & SELECTION
const isStatusColumn = (key) => {
  return key === 'status' || key === meta.value?.status_field
}

const formatCellValue = (val, fieldtype) => {
  if (val === null || val === undefined || val === '') return '—'
  if (fieldtype === 'Datetime') {
    try {
      const d = new Date(val)
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    } catch (e) {
      return String(val)
    }
  }
  if (fieldtype === 'Date') {
    try {
      const d = new Date(val)
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
    } catch (e) {
      return String(val)
    }
  }
  if (fieldtype === 'Currency') {
    try {
      return new Intl.NumberFormat('en-AE', { style: 'currency', currency: 'AED' }).format(val)
    } catch (e) {
      return `AED ${val}`
    }
  }
  if (fieldtype === 'Percent') {
    return `${val}%`
  }
  return String(val)
}

const toggleRowSelect = (name) => {
  if (selectedRowNames.value.includes(name)) {
    selectedRowNames.value = selectedRowNames.value.filter(n => n !== name)
  } else {
    selectedRowNames.value.push(name)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedRowNames.value = []
  } else {
    selectedRowNames.value = rows.value.map(r => r.name)
  }
}

const clearSelection = () => {
  selectedRowNames.value = []
}

// ACTIONS
const openCreateForm = () => {
  emit('open-create', props.docType)
}

const openDocument = (docType, name) => {
  const currentPath = route.path
  const base = currentPath.substring(0, currentPath.lastIndexOf('/'))
  const slug = currentPath.substring(currentPath.lastIndexOf('/') + 1)
  router.push(`${base}/${slug}/${encodeURIComponent(name)}`)
}

const handleRowClick = (row) => {
  emit('row-click', row)
  openDocument(props.docType, row.name)
}

const confirmDeleteRow = async (row) => {
  if (!confirm(`Are you sure you want to delete ${props.docType} record "${row.name}"?`)) return
  try {
    const res = await deleteDocument(props.docType, row.name)
    if (res.success) {
      notificationStore.showSuccess('Deleted', `${props.docType} "${row.name}" deleted successfully.`)
      loadData()
    } else {
      notificationStore.showError('Delete Failed', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Delete Error', extractFrappeErrorMessage(null, err))
  }
}

const performBulkDelete = async () => {
  if (!confirm(`Are you sure you want to delete ${selectedRowNames.value.length} selected ${props.docType} records?`)) return
  try {
    const res = await deleteDocumentsBulk(props.docType, selectedRowNames.value)
    if (res.success) {
      const deletedCount = res.data?.deleted?.length || 0
      notificationStore.showSuccess('Bulk Delete Complete', `Successfully deleted ${deletedCount} records.`)
      selectedRowNames.value = []
      loadData()
    } else {
      notificationStore.showError('Bulk Delete Error', extractFrappeErrorMessage(res, null))
    }
  } catch (err) {
    notificationStore.showError('Bulk Delete Error', extractFrappeErrorMessage(null, err))
  }
}

const exportToCSV = () => {
  if (rows.value.length === 0) return
  const cols = activeColumns.value
  const headers = cols.map(c => `"${c.label}"`).join(',')
  const csvRows = rows.value.map(row => {
    return cols.map(c => {
      const val = row[c.key]
      const cleanVal = val === null || val === undefined ? '' : String(val).replace(/"/g, '""')
      return `"${cleanVal}"`
    }).join(',')
  })
  const csvContent = "data:text/csv;charset=utf-8," + [headers, ...csvRows].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  link.setAttribute("download", `${props.docType}_export_${new Date().toISOString().slice(0,10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const goToPage = (newPage) => {
  if (newPage < 1 || newPage > maxPage.value) return
  page.value = newPage
  loadData()
}

const onPageSizeChange = (e) => {
  pageSize.value = Number(e.target.value)
  page.value = 1
  loadData()
}

// LIFECYCLE & WATCHERS
watch(() => props.docType, async (newVal) => {
  if (newVal) {
    page.value = 1
    searchText.value = ''
    activeFilters.value = []
    selectedRowNames.value = []
    await loadMeta()
    await loadData()
  }
})

onMounted(async () => {
  await loadMeta()
  await loadData()
})
</script>
