import DonutLabels from "@/components/ui/DonutLabels";

import AreaChartCom from "@/components/ui/AreaChart";
import Barchart from "@/components/ui/BarChart";
import React from "react";

import EditableDropdown from "../components/ui/EditableDropdown";
import CustomChart from "@/components/ui/CustomChart";
import RadialChart from "@/components/ui/RadialChart";
import WorkBarChart from "@/components/ui/WorkBarChart";
import WorkDoneList from "@/components/ui/WorkDoneList";
import AssignTaskList from "@/components/ui/AssignTaskList";

const ChartsPage = () => {
  const [selectedProjectId, setSelectedProjectId] = React.useState(0);

  return (
    <>
      <EditableDropdown setSelectedProjectId={setSelectedProjectId} />
      <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
        <div className="flex flex-col gap-4 w-1/2 h-full">
          <DonutLabels selectedProjectId={selectedProjectId} />
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
    </>
  );
};

export default ChartsPage;
