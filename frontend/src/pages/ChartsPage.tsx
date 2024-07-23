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
import MultiCharts  from "@/components/_charts/MultiCharts";

const sevenDaysAgo = () => {
  const date = new Date();
  date.setDate(date.getDate() - 7);
  return date;
};

const ChartsPage = () => {
  const [selectedProjectId, setSelectedProjectId] = React.useState(0);
  const [date, setDate] = React.useState<DateRange>({
    from: sevenDaysAgo(),
    to: new Date(),
  });

  return (
    <>
      <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
        <EditableDropdown setSelectedProjectId={setSelectedProjectId} />
        <DatePickerWithRange date={date} setDate={setDate} />
      </div>
      <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <DonutLabels selectedProjectId={selectedProjectId} dateRange={date} />
        </div>
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <AreaChartCom selectedProjectId={selectedProjectId} />
        </div>
      </div>
      <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <Barchart selectedProjectId={selectedProjectId} />
        </div>
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <CustomChart selectedProjectId={selectedProjectId} />
        </div>
      </div>
      <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <RadialChart selectedProjectId={selectedProjectId} />
        </div>
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <WorkBarChart selectedProjectId={selectedProjectId} />
        </div>
      </div>
      <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <WorkDoneList selectedProjectId={selectedProjectId} />
        </div>
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <AssignTaskList selectedProjectId={selectedProjectId} />
        </div>
      </div>
      <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <MultiCharts selectedProjectId={selectedProjectId} />
        </div>
      </div>
    </>
  );
};

export default ChartsPage;
