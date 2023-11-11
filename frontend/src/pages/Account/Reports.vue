<template>
  <div class="account-internal-padding account-reports">
    <h1 class="heading">Reports</h1>
    <div class="account-sub-block">
      <UPreloader v-if="!Account.Reports.dto" mode="reportsFilters" :activation="true" />
      <div v-else class="flex report-filter">
        <URadioChip v-model="reportFilter" name="report-filter-chip" value="all">All</URadioChip>
        <URadioChip v-model="reportFilter" name="report-filter-chip" value="rent_analyzer">Rent Analyzer Report</URadioChip>
        <URadioChip v-model="reportFilter" name="report-filter-chip" value="property">Property Report</URadioChip>
      </div>
      <template v-if="!Account.Reports.dto">
        <UPreloader mode="reportsHeadings" :activation="true" />
        <UPreloader v-for="i of 3" :key="i" mode="reports" :activation="true" />
      </template>
      <table v-else class="ui-table ui-table--stripped ui-table--mobile-transform">
        <tr>
          <th>Address</th>
          <th>Beds/Bath</th>
          <th>Report Type</th>
          <th>Date Saved</th>
          <th></th>
        </tr>
        <tr v-for="report of filteredReports" :key="report">
          <td data-desc="Property">{{ report?.list_data?.address || 'N/A' }}</td>
          <td data-desc="Beds">{{ report?.list_data?.beds || 'N/A' }}/{{ report?.list_data?.baths || 'N/A'}}</td>
          <td data-desc="Report Type">{{ getReportTypeName(report) }} Report</td>
          <td data-desc="Creation Date">{{ $format['date'](report.created_at) }}</td>
          <td>
            <a :href="report.report_file" class="ui-href ui-href-default link-open" target="_blank">Open</a>
            <a :href="report.report_file" download class="ui-href ui-href-default" target="_blank">Download</a>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<style lang="less" scoped>
.account-reports {
  
  .account-sub-block { padding: 0; }
  .report-filter {
    padding: 20px 30px 5px;
    overflow-x: auto;

    .ui-radio-chip {
      flex: 0 0 auto;
    }
    @media @mobile { padding: 20px 20px 10px; }
  }
  .ui-table {
    .ui-href-default + .ui-href-default { margin-left: 10px; }
    .link-open {
      color: @col-text-gray-darker;
      text-decoration: none;

      &:hover, &:focus { color: @col-text-gray-dark; }
    }

    @media @mobile {
      tr {
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 10px 10px;
        grid-template-areas:
        'a a a b'
        'r r d d'
        'l l l l';

        td:nth-child(1) { grid-area: a; }
        td:nth-child(2) { grid-area: b; }
        td:nth-child(3) { grid-area: r; }
        td:nth-child(4) { grid-area: d; }
        td:nth-child(5) { grid-area: l; }
      }
    }
  }
}
</style>

<script lang="ts">
import { defineComponent } from 'vue';

import URadioChip from '@/components/ui/URadioChip.vue';
import UPreloader from '@/components/ui/UPreloader.vue';
import AccountStore from '@/models/Account';
import { TReportDTO__ListItem } from '@/models/Reports/api';

export default defineComponent({
  components: {
    URadioChip,
    UPreloader
  },
  computed: {
    Account() { return AccountStore; },
    filteredReports() {
      if (!AccountStore.Reports.dto)
        return [];

      //@ts-ignore VUE FIX WTF?
      return this.reportFilter == 'all' ? AccountStore.Reports.dto : AccountStore.Reports.dto.filter(r => {
        //@ts-ignore VUE FIX WTF?
        return r.report_type == this.reportFilter;
      });
      
    }
  },
  data() {
    return {
      reportFilter: 'all'
    }
  },
  methods: {
    getReportTypeName(report: TReportDTO__ListItem) {
      if (report.report_type == 'rent_analyzer')
        return 'Rent Analyzer';

      if (report.report_type == 'property')
        return 'Property';

      return 'Unknown';
    }
  },
  mounted() {
    AccountStore.Reports.load().catch(ex => console.error(ex));
  }
})
</script>