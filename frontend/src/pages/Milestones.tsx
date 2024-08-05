import React, { useState } from "react";

import EditableDropdown from "../components/_ui/EditableDropdown";

import { DatePickerWithRange } from "@/utils/DateRange";
import IssueTable from "@/components/_ui/IssueTable";
import MileStoneTable from "@/components/_ui/MilestoneTable";
import { Milestone } from "lucide-react";

const sevenDaysAgo = () => {
  const date = new Date();
  date.setDate(date.getDate() - 7);
  return date;
};

const Milestones = () => {
  const [selectedProjectId, setSelectedProjectId] = React.useState(0);
  const [selectedOption, setSelectedOption] = useState("ongoing_milestones");
  const [date, setDate] = React.useState({
    from: sevenDaysAgo(),
    to: new Date(),
  });

  function handleClick(filter_name: string): any {
    setSelectedOption(filter_name);
  }

  const time = "2 Hours";

  return (
    <>
      <div className="container mx-auto p-4 flex flex-row gap-4 h-full w-full">
        <EditableDropdown setSelectedProjectId={setSelectedProjectId} />
        {/* <DatePickerWithRange dateRange={date} setDateRange={setDate} /> */}
      </div>

      <nav className="bg-white border-gray-200 dark:bg-gray-900">
        <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
          <div
            className="items-center justify-between hidden w-full md:flex md:w-auto md:order-1"
            id="navbar-search"
          >
            <ul className="flex flex-col p-4 md:p-0 mt-4 font-medium border border-gray-100 rounded-lg bg-gray-50 md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
              <li onClick={() => setSelectedOption("ongoing_milestones")}>
                <div
                  className={`px-4 py-2 rounded-full ${
                    selectedOption === "ongoing_milestones"
                      ? "bg-purple-600 text-white"
                      : "bg-gray-200 text-gray-700"
                  }`}
                >
                  <span className="font-semibold">On-Going</span>
                  <span className="ml-2">{time}</span>
                </div>
              </li>
              <li onClick={() => setSelectedOption("completed_milestones")}>
                <div
                  className={`px-4 py-2 rounded-full ${
                    selectedOption === "completed_milestones"
                      ? "bg-purple-600 text-white"
                      : "bg-gray-200 text-gray-700"
                  }`}
                >
                  <span className="font-semibold">Closed</span>
                </div>
              </li>
              <li onClick={() => setSelectedOption("all_milestones")}>
                <div
                  className={`px-4 py-2 rounded-full ${
                    selectedOption === "all_milestones"
                      ? "bg-purple-600 text-white"
                      : "bg-gray-200 text-gray-700"
                  }`}
                >
                  <span className="font-semibold">All</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {
        <MileStoneTable
          selectedProjectId={selectedProjectId}
          selectedOption={selectedOption}
        />
      }
    </>
  );
};

export default Milestones;
