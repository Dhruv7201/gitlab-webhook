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

  return (
    <>
      <div className="p-4">
        <div className="mx-auto flex flex-row gap-4 mb-4">
          <EditableDropdown setSelectedProjectId={setSelectedProjectId} />
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
                    className={`px-4 py-2 rounded-full cursor-pointer ${
                      lableName === ""
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    <span className="font-semibold">Issues</span>
                  </div>
                </li>
                <li onClick={() => setLableName("Documentation")}>
                  <div
                    className={`px-4 py-2 rounded-full cursor-pointer ${
                      lableName === "Documentation"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    <span className="font-semibold">Plan</span>
                  </div>
                </li>
                <li onClick={() => setLableName("Doing")}>
                  <div
                    className={`px-4 py-2 rounded-full cursor-pointer ${
                      lableName === "Doing"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    <span className="font-semibold">Doing</span>
                  </div>
                </li>
                <li onClick={() => setLableName("Testing")}>
                  <div
                    className={`px-4 py-2 rounded-full cursor-pointer ${
                      lableName === "Testing"
                        ? "bg-blue-600 text-white"
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

        <IssueTable
          selectedProjectId={selectedProjectId}
          lableName={lableName}
        />
      </div>
    </>
  );
};

export default FilterPage;
