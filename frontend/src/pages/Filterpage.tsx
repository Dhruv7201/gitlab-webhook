import React from "react";

import EditableDropdown from "../components/_ui/EditableDropdown";

import { DatePickerWithRange } from "@/utils/DateRange";
import IssueTable from "@/components/_ui/IssueTable";

const sevenDaysAgo = () => {
  const date = new Date();
  date.setDate(date.getDate() - 7);
  return date;
};

const FilterPage = () => {
  const [selectedProjectId, setSelectedProjectId] = React.useState(0);
  const [lableName, setLableName] = React.useState("");
  const [date, setDate] = React.useState({
    from: sevenDaysAgo(),
    to: new Date(),
  });

  function handleClick(filter_name: string): any {
    setLableName(filter_name);
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
              <li onClick={() => setLableName("")}>
                <div
                  className={`px-4 py-2 rounded-full ${
                    lableName === ""
                      ? "bg-purple-600 text-white"
                      : "bg-gray-200 text-gray-700"
                  }`}
                >
                  <span className="font-semibold">Issues</span>
                  <span className="ml-2">{time}</span>
                </div>
              </li>
              <li onClick={() => setLableName("Documentation")}>
                <div
                  className={`px-4 py-2 rounded-full ${
                    lableName === "Documentation"
                      ? "bg-purple-600 text-white"
                      : "bg-gray-200 text-gray-700"
                  }`}
                >
                  <span className="font-semibold">Plan</span>
                </div>
              </li>
              <li onClick={() => setLableName("Doing")}>
                <div
                  className={`px-4 py-2 rounded-full ${
                    lableName === "Doing"
                      ? "bg-purple-600 text-white"
                      : "bg-gray-200 text-gray-700"
                  }`}
                >
                  <span className="font-semibold">Doing</span>
                </div>
              </li>
              <li onClick={() => setLableName("Testing")}>
                <div
                  className={`px-4 py-2 rounded-full ${
                    lableName === "Testing"
                      ? "bg-purple-600 text-white"
                      : "bg-gray-200 text-gray-700"
                  }`}
                >
                  <span className="font-semibold">Testing</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {
        <IssueTable
          selectedProjectId={selectedProjectId}
          lableName={lableName}
        />
      }
    </>
  );
};

export default FilterPage;
