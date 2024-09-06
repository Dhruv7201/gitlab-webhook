import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api, { validateToken } from "@/utils/api";
import { FileText, HelpCircle, UserIcon } from "lucide-react";

const Settings = () => {
  const [labels, setLabels] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem("token")) {
      validateToken(localStorage.getItem("token") as string).then((res) => {
        if (!res) {
          localStorage.removeItem("token");
          navigate("/login");
        }
      });
    } else {
      navigate("/login");
    }
  }, [navigate]);

  useEffect(() => {
    const fetchLabels = async () => {
      const response = await api.get("/labels");
      setLabels(response.data);
    };
    fetchLabels();
  }, []);

  const handleToggle = async (
    labelName: string,
    type: "user" | "issue",
    enabled: boolean
  ) => {
    try {
      await api.post(`/toggle-label`, {
        label: labelName,
        type,
        enabled,
      });

      setLabels((prevLabels) =>
        prevLabels.map((label) =>
          label.name === labelName
            ? {
                ...label,
                [`${type}_enabled`]: enabled,
              }
            : label
        )
      );
    } catch (error) {
      console.error("Error toggling label:", error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Label Settings</h1>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {labels.map((label) => (
          <div
            key={label.id}
            className="bg-white shadow-lg rounded-lg p-4 flex flex-col space-y-4"
          >
            <div className="flex items-center space-x-3">
              <span
                style={{ backgroundColor: label.color }}
                className="w-4 h-4 rounded-full"
              ></span>

              <h2 className="text-lg font-semibold">{label.name}</h2>

              {label.description && (
                <div className="relative group">
                  <HelpCircle className="text-gray-400 hover:text-gray-700 cursor-pointer" />
                  <div className="absolute bottom-0 left-6 hidden w-60 p-2 bg-gray-200 text-gray-800 text-sm rounded-lg shadow-md group-hover:block">
                    {label.description}
                  </div>
                </div>
              )}
            </div>

            <div className="flex flex-col space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-gray-700 flex items-center">
                  User Label Tracing
                  <UserIcon size={16} className="ml-2" />
                </label>
                <input
                  type="checkbox"
                  className="toggle-checkbox"
                  checked={label.user_enabled}
                  onChange={(e) =>
                    handleToggle(label.name, "user", e.target.checked)
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="text-gray-700 flex items-center">
                  Issue Label Tracing <FileText size={16} className="ml-2" />
                </label>
                <input
                  type="checkbox"
                  className="toggle-checkbox"
                  checked={label.issue_enabled}
                  onChange={(e) =>
                    handleToggle(label.name, "issue", e.target.checked)
                  }
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Settings;
