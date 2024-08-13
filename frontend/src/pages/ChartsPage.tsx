import DonutLabels from "@/components/_charts/DonutLabels";
import AreaChartCom from "@/components/_charts/AreaChart";
import Barchart from "@/components/_charts/BarChart";
import React, { useEffect } from "react";
import EditableDropdown from "../components/_ui/EditableDropdown";
import CustomChart from "@/components/_charts/CustomChart";
import WorkBarChart from "@/components/_charts/WorkBarChart";
import WorkDoneList from "@/components/_tables/WorkDoneList";
import AssignTaskList from "@/components/_tables/AssignTaskList";
import { DatePickerWithRange } from "@/utils/DateRange";
import { DateRange } from "react-day-picker";
import { MultiBarChart } from "@/components/_charts/MultiBarchart";
import IssuesLifeTime from "@/components/_charts/IssuesLifeTime";
import { Button } from "@/components/_ui/button";
import { MonitorDown } from "lucide-react";

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

  const dailyReportDownload = () => {
    const api = import.meta.env.VITE_API_URL;
    window.open(`${api}/daily_work_report`);
  };

  const handleReset = () => {
    setDate({
      from: monthAgo(),
      to: new Date(),
    });
    setSelectedProjectId(0);
  };

  useEffect(() => {
    if (localStorage.getItem("selectedProjectId")) {
      setSelectedProjectId(Number(localStorage.getItem("selectedProjectId")));
    } else {
      setSelectedProjectId(0);
      localStorage.setItem("selectedProjectId", "0");
    }
  }, []);

  return (
    <>
      <div className="p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between md:gap-4 gap-2">
          <EditableDropdown
            setSelectedProjectId={setSelectedProjectId}
            selectedProjectId={selectedProjectId}
          />
          <DatePickerWithRange date={date} setDate={setDate} />
          <div className="flex flex-col md:flex-row md:ml-auto md:gap-4 gap-2">
            <div className="flex gap-2 md:ml-auto">
              <Button onClick={handleReset} className="bg-blue-600">
                Reset
              </Button>
              <Button className="bg-blue-600" onClick={dailyReportDownload}>
                Export Report
                <MonitorDown size={16} className="ml-2" />
              </Button>
            </div>
          </div>
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
