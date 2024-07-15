import * as React from "react";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";
import Notification from "../../Notification";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

type Project = {
  id: string;
  name: string;
};

type ChartData = {
  user: string;
  completed_issues: number;
  assigned_issues: number;
};

const chartConfig = {

  mobile: {
    label: "assigned_issues",
    color: "hsl(var(--chart-2))",
  },
  desktop: {
    label: "completed_issues",
    color: "hsl(var(--chart-1))",
  },
} as ChartConfig;

export function AreaChartCom() {
  const [chartData, setChartData] = React.useState<ChartData[]>([]);
  const [projects, setProjects] = React.useState<Project[]>([]);
  const api = import.meta.env.VITE_API_URL;

  React.useEffect(() => {
    const get_projects = async ()=>{
    try {
      const response = await fetch(api + "/projects");
      const data = await response.json();
      setProjects(data.data);
    } catch (error) {
      Notification({ message: "Problem fetching users", type: "error" });
    }
  }
  get_projects()
  }, []);


  const fetchData = async (project_id: any) => {
    
    try {
      // const project_id = 59516973
      const response = await fetch(api + `/user_activity_chart/${project_id}`);
      const data = await response.json();
      console.log(data);

      // Transform the API response into the format expected by Recharts
      const transformedData = data.labels.map(
        (label: string, index: number) => ({
          user: label,
          completed_issues: data.completed_issues[index],
          assigned_issues: data.assigned_issues[index],
        })
      );

      setChartData(transformedData);
    } catch (error) {
      console.error("Problem fetching data", error);
    }
  }
 



  return (
    <Card>
      <select
        defaultValue=""
        onChange={(e) => fetchData(e.target.value)}
        className="block py-2 px-4 rounded-md shadow-sm border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 w-48"
      >
        <option value="" disabled>
          Choose user
        </option>
        {projects.map((project) => (
          <option key={project.id} value={project.id} className="text-gray-900">
            {project.name}
          </option>
        ))}
      </select>
      <CardHeader>
        <CardTitle>Area Chart - Stacked</CardTitle>
        <CardDescription>
          Showing total users and their assigned issues
        </CardDescription>
      </CardHeader>
      <CardContent>
      
        <ChartContainer config={chartConfig}>
          
          <AreaChart
            accessibilityLayer
            data={chartData}
            margin={{
              left: 20,
              right: 20,
            }}
          >
            
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="user"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Area
              dataKey="completed_issues"
              type="natural"
              fill="var(--color-desktop)"
              fillOpacity={0.4}
              stroke="var(--color-desktop)"
              stackId="a"
            />
            
            <Area
              dataKey="assigned_issues"
              type="natural"
              fill="var(--color-mobile)"
              fillOpacity={0.4}
              stroke="var(--color-mobile)"
              stackId="a"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
