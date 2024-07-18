"use client";
import Notification from "../../Notification";
import * as React from "react";
import { ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Command } from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

type Project = {
  id: number;
  name: string;
};
interface Props {
  setSelectedProjectId: (id: number) => void;
}

const EditableDropdown: React.FC<Props> = ({ setSelectedProjectId }) => {
  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState("");
  const [availableProject, setAvailableProject] = React.useState(false);
  const [_openInputTag, setInputTag] = React.useState(true);

  const [projects, setProjects] = React.useState<Project[]>([]);
  const api = import.meta.env.VITE_API_URL;
  React.useEffect(() => {
    const get_projects = async () => {
      try {
        const response = await fetch(api + "/projects");

        const data = await response.json();
        setProjects(data.data);
      } catch (error) {
        Notification({ message: "Problem fetching users", type: "error" });
      }
    };
    get_projects();
  }, []);

  function onSearchButtonClick(project: { id: number; name: any }) {
    setSelectedProjectId(Number(project.id));
    setValue(project.name);
    setInputTag(false);
    setOpen(false);
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          className="w-[200px] justify-between"
          onClick={() => setInputTag(true)}
          aria-expanded="true"
          data-state="opened"
        >
          {value
            ? projects.find((framework) => framework.name === value)?.name
            : "Select Project"}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <div>
            <input
              type="text"
              autoFocus
              onChange={(e) => {
                setAvailableProject(false);
                setValue(e.target.value);
              }}
              value={value}
            />
            <div>
              {projects
                .filter((item) => {
                  if (value == "") {
                    return true;
                  }
                  const input_value = value.toLowerCase();
                  const item_value = item.name.toLowerCase();
                  return input_value && item_value.startsWith(input_value);
                })
                .map((project) => (
                  <>
                    {availableProject === false
                      ? setAvailableProject(true)
                      : null}
                    <h1
                      onClick={() => {
                        onSearchButtonClick(project);
                      }}
                    >
                      {project.name}
                    </h1>
                  </>
                ))}
              {availableProject === false ? "No Project Found" : ""}
            </div>
          </div>
        </Command>
      </PopoverContent>
    </Popover>
  );
};
export default EditableDropdown;
