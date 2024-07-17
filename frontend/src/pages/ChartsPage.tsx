import { DonutLabels } from "@/components/ui/DonutLabels";
import { AreaChartCom } from "@/components/ui/AreaChart";
import { Barchart } from "@/components/ui/BarChart";
import React, { useState, useEffect } from 'react';


import EditableDropdown from "../components/ui/EditableDropdown";

const ChartsPage = () => {
  const [project_id, setProjectId] = useState()
  const [selected, setSelected] = useState(false)
  return (
    <>
    <EditableDropdown />
    <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
      <div className="flex flex-col gap-4 w-1/2 h-full">
        {/* <DonutLabels  project_id={project_id} selected={selected}/> */}
      </div>
      <div className="flex flex-col gap-4 w-1/2 h-full">
        <AreaChartCom />
      </div>
      </div>
      <div className="row">
      <div className="flex flex-col gap-4 w-1/2 h-full">
        <Barchart />
      </div>
      </div>
      </>
  );
};

export default ChartsPage;
