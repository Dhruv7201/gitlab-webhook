import { ArrowDown, LayoutDashboard, Milestone } from "lucide-react";
import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";

const Layout = ({ children }: { children: React.ReactNode }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <div className="flex h-screen">
      <aside
        className={`fixed top-0 left-0 h-full bg-blue-600 text-gray-200 transition-transform transform ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0 md:w-64 z-30 shadow-lg md:shadow-none`}
        aria-label="Sidebar"
      >
        <div className="p-4">
          <h1 className="text-3xl font-bold mb-6">
            <NavLink to="/dashboard" className="text-white hover:text-gray-300">
              Git Analytics
            </NavLink>
          </h1>
          <nav>
            <ul className="space-y-2">
              <li>
                <NavLink
                  to="/dashboard"
                  className={({ isActive }) =>
                    `py-3 px-4 rounded-md flex items-center space-x-3 text-lg ${
                      isActive ? "bg-gray-800" : "hover:bg-gray-700"
                    }`
                  }
                >
                  <LayoutDashboard size={24} />
                  <span>Dashboard</span>
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/milestones"
                  className={({ isActive }) =>
                    `py-3 px-4 rounded-md flex items-center space-x-3 text-lg ${
                      isActive ? "bg-gray-800" : "hover:bg-gray-700"
                    }`
                  }
                >
                  <Milestone size={24} />
                  <span>Milestones</span>
                </NavLink>
              </li>
              <li>
                <div className="relative">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="py-3 px-4 rounded-md flex items-center space-x-3 text-lg hover:bg-gray-700 w-full"
                  >
                    <span>More</span>
                    <ArrowDown
                      className={`ml-auto transition-transform absolute right-4 ${
                        dropdownOpen ? "rotate-180" : ""
                      }`}
                    />
                  </button>

                  <div
                    className={`absolute  mt-2 bg-gray-800 text-white w-full rounded-md shadow-lg transition-transform duration-300 ease-in-out ${
                      dropdownOpen
                        ? "max-h-screen opacity-100 scale-100"
                        : "max-h-0 opacity-0 scale-95"
                    } overflow-hidden`}
                  >
                    <ul className="space-y-1">
                      <li>
                        <Link
                          to="/settings"
                          className="block py-3 px-4 hover:bg-gray-600"
                        >
                          Settings
                        </Link>
                      </li>
                      <li>
                        <Link
                          to="/profile"
                          className="block py-3 px-4 hover:bg-gray-600"
                        >
                          Profile
                        </Link>
                      </li>
                    </ul>
                  </div>
                </div>
              </li>
            </ul>
          </nav>
        </div>
      </aside>
      <main className="flex-1 ml-0 md:ml-64">{children}</main>
    </div>
  );
};

export default Layout;
