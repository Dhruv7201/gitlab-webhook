import React from "react";
import EditableDropdown from "../components/_ui/EditableDropdown";
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
        {/* Dropdown for selecting projects */}
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <EditableDropdown
            setSelectedProjectId={setSelectedProjectId}
            selectedProjectId={selectedProjectId}
          />
        </div>

        {/* Navbar for filtering options */}
        <nav className="bg-white border-gray-200 dark:bg-gray-900">
          <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
            {/* Navbar items */}
            <div className="w-full md:w-auto">
              <ul className="flex flex-col md:flex-row p-4 md:p-0 font-medium bg-gray-50 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
                <li className="md:mr-2 mb-2 md:mb-0">
                  <div
                    className={`px-4 py-2 rounded-full cursor-pointer ${
                      lableName === ""
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                    onClick={() => setLableName("")}
                  >
                    <span className="font-semibold">Issues</span>
                  </div>
                </li>
                <li className="md:mr-2 mb-2 md:mb-0">
                  <div
                    className={`px-4 py-2 rounded-full cursor-pointer ${
                      lableName === "Documentation"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                    onClick={() => setLableName("Documentation")}
                  >
                    <span className="font-semibold">Plan</span>
                  </div>
                </li>
                <li className="md:mr-2 mb-2 md:mb-0">
                  <div
                    className={`px-4 py-2 rounded-full cursor-pointer ${
                      lableName === "Doing"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                    onClick={() => setLableName("Doing")}
                  >
                    <span className="font-semibold">Doing</span>
                  </div>
                </li>
                <li className="md:mr-2 mb-2 md:mb-0">
                  <div
                    className={`px-4 py-2 rounded-full cursor-pointer ${
                      lableName === "Testing"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                    onClick={() => setLableName("Testing")}
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
