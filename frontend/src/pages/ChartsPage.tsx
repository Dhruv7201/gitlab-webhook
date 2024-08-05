import DonutLabels from "@/components/_charts/DonutLabels";
import AreaChartCom from "@/components/_charts/AreaChart";
import Barchart from "@/components/_charts/BarChart";
import React from "react";
import EditableDropdown from "../components/_ui/EditableDropdown";
import CustomChart from "@/components/_charts/CustomChart";
import RadialChart from "@/components/_charts/RadialChart";
import WorkBarChart from "@/components/_charts/WorkBarChart";
import WorkDoneList from "@/components/_tables/WorkDoneList";
import AssignTaskList from "@/components/_tables/AssignTaskList";
import { DatePickerWithRange } from "@/utils/DateRange";
import { DateRange } from "react-day-picker";
import { MultiBarChart } from "@/components/_charts/MultiBarchart";
import IssuesLifeTime from "@/components/_charts/IssuesLifeTime";

const monthAgo = () => {
  const date = new Date();
  date.setMonth(date.getMonth() - 1);
  return date;
};

const ChartsPage = () => {
  const [selectedProjectId, setSelectedProjectId] = React.useState(0);
  const [date, setDate] = React.useState<DateRange>({
    from: monthAgo(),
    to: new Date(),
  });

  return (
    <>
      <div className="p-4">
        <div className="flex gap-4 mb-4">
          <EditableDropdown setSelectedProjectId={setSelectedProjectId} />
          <DatePickerWithRange date={date} setDate={setDate} />
        </div>
      </div>

      <div className="space-y-4 p-4">
        <IssuesLifeTime
          selectedProjectId={selectedProjectId}
          dateRange={date}
        />
        <AreaChartCom selectedProjectId={selectedProjectId} dateRange={date} />
        <Barchart selectedProjectId={selectedProjectId} dateRange={date} />
        <CustomChart selectedProjectId={selectedProjectId} dateRange={date} />
        <MultiBarChart project_id={selectedProjectId} dateRange={date} />
        <WorkBarChart selectedProjectId={selectedProjectId} dateRange={date} />
        <WorkDoneList selectedProjectId={selectedProjectId} dateRange={date} />
        <AssignTaskList
          selectedProjectId={selectedProjectId}
          dateRange={date}
        />
        <DonutLabels selectedProjectId={selectedProjectId} dateRange={date} />
      </div>
    </>
  );
};

export default ChartsPage;
