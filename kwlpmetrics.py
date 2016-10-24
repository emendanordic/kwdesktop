
import csv, os, sys
from collections import namedtuple

METRIC_KIND_ID = 0
METRIC_KIND_REF = 1
METRIC_KIND_DESCRIPTION = 2

METRIC_LOC_ID = 0
METRIC_ID = 1
METRIC_VALUE = 2

FILE_LOC_ID = 0
FILE_PATH = 1

ENTITY_LOC_ID = 0
ENTITY_NAME = 3
ENTITY_DEP_ID = 4
ENTITY_FILE = 5

ATTRIBUTE_LOC_ID = 0
ATTRIBUTE_ATTRIBUTE = 1
ATTRIBUTE_VALUE = 2

MetricId = namedtuple("MetricId", "loc_id metric_id")
Entity = namedtuple("Entity", "id name dep_id file_name")
MetricKind = namedtuple("MetricKind", "id ref description")
Metric = namedtuple("Metric", "id metric_id value")
File = namedtuple("File", "id path")
Attribute = namedtuple("Attribute", "id attribute value")

FileMetrics = namedtuple("FileMetrics", "file_path funcs classes metrics")
FuncMetrics = namedtuple("FuncMetrics", "name metrics")
ClassMetrics = namedtuple("ClassMetrics", "name metrics")

class KwLocalProjectMetrics:

    def __init__(self, project_dir, metrics_report, metrics_ref):
        self.project_dir = project_dir
        self.metrics_report = metrics_report
        self.metrics_dir = os.path.join(project_dir, 'workingcache', 'tables')
        self.metrics_ref = metrics_ref.strip().split(',')
        self.metrics_ref_ids = [] # to store ids of wanted metrics
        self.has_func_metrics = False
        self.has_class_metrics = False

        self.file_metrics_db = dict()

        self.metric_kind_dict = dict()
        self.metric_dict = dict()
        self.file_dict = dict()
        self.entity_dict = dict()
        self.attribute_dict = dict()

        self.metric_dat = os.path.join(self.metrics_dir, 'metric.dat')
        self.metric_kind_dat = os.path.join(self.metrics_dir, 'metric_kind.dat')
        self.file_dat = os.path.join(self.metrics_dir, 'file.dat')
        self.entity_dat = os.path.join(self.metrics_dir, 'entity.dat')
        self.attribute_dat = os.path.join(self.metrics_dir, 'attribute.dat')

    def generate_report(self):
        # TODO : error handling
        self.parse_metric_kinds_dat()
        self.get_metric_ids() # needs to be done before we parse the metrics
        self.parse_metric_dat()
        self.parse_file_dat()
        self.parse_entity_dat()
        self.parse_attribute_dat()

        self.process_metrics()

        self.write_to_csv()

    def write_to_csv(self):
        title = ["File"]
        if self.has_func_metrics: title.append("Func")
        if self.has_class_metrics: title.append("Class")
        title += self.metrics_ref
        data = []
        data.append(title)
        for file_metric in self.file_metrics_db.values():
            col = [file_metric.file_path]
            if self.has_func_metrics: col.append("")
            if self.has_class_metrics: col.append("")

            col += self.get_csv_metric_values(file_metric.metrics)

            data.append(col)
            for func_metric in file_metric.funcs.values():
                col = [file_metric.file_path, func_metric.name]
                if self.has_class_metrics: col.append("")
                col += self.get_csv_metric_values(func_metric.metrics)
                data.append(col)

            for class_metric in file_metric.classes.values():
                col = [file_metric.file_path]
                if self.has_func_metrics: col.append("")
                col.append(class_metric.name)
                col += self.get_csv_metric_values(class_metric.metrics)
                data.append(col)
        print data
        with open(self.metrics_report, 'w') as fp:
            a = csv.writer(fp, delimiter=';')
            a.writerows(data)

    def get_csv_metric_values(self, metrics):
        metric_values = [""] * len(self.metrics_ref)
        for metric in metrics:
            print metric
            print self.metrics_ref_ids
            index = self.metrics_ref_ids.index(metric.metric_id)
            metric_values[index] = metric.value
        print metric_values
        return metric_values


    def process_metrics(self):
        for metrics in self.metric_dict.values():
            for metric in metrics:
                if metric.id in self.attribute_dict:
                    attr = self.attribute_dict[metric.id]
                    if 'header-location' in attr.attribute and 'system' in attr.value:
                        continue
                # else we have a file or func that we care about
                file_id = self.get_file_id_from_loc_id(metric.id)
                file_path = self.file_dict[file_id]
                file_metric = self.file_metrics_db.setdefault(
                    file_id, FileMetrics(file_path=file_path, funcs=dict(),
                    classes=dict(), metrics=[])
                )

                if file_id == metric.id:
                    # then this is a file
                    file_metric.metrics.append(metric)
                else:
                    name = self.entity_dict[metric.id].name
                    # the entity is a func/class
                    if metric.id in self.attribute_dict:
                        self.has_func_metrics = True
                        file_metric.funcs.setdefault(
                            metric.id, FuncMetrics(name=name, metrics=[])
                        ).metrics.append(metric)
                    else:
                        self.has_class_metrics = True
                        file_metric.classes.setdefault(
                            metric.id, ClassMetrics(name=name, metrics=[])
                        ).metrics.append(metric)

    def get_metric_ids(self):
        for i in self.metrics_ref:
            if not i in self.metric_kind_dict:
                sys.exit('Could not find metrics ref {0}'.format(i))
            self.metrics_ref_ids.append(self.metric_kind_dict[i].id)

    def get_file_id_from_loc_id(self, loc_id):
        return self.entity_dict[loc_id].file_name

    def parse_metric_kinds_dat(self):
        with open(self.metric_kind_dat, 'r') as f:
            for line in [l.strip().split(';') for l in f]:
                self.metric_kind_dict[line[METRIC_KIND_REF]] = MetricKind(id=line[METRIC_KIND_ID],
                ref=line[METRIC_KIND_REF], description=line[METRIC_KIND_DESCRIPTION])

    def parse_metric_dat(self):
        with open(self.metric_dat, 'r') as f:
            for line in [l.strip().split(';') for l in f]:
                if line[METRIC_ID] in self.metrics_ref_ids:
                    self.metric_dict.setdefault(line[METRIC_ID], []).append(
                        Metric(id=line[METRIC_LOC_ID] , metric_id=line[METRIC_ID],
                    value=line[METRIC_VALUE]))

    def parse_file_dat(self):
        with open(self.file_dat, 'r') as f:
            for line in [l.strip().split(';') for l in f]:
                self.file_dict[line[FILE_LOC_ID]] = line[FILE_PATH]

    def parse_entity_dat(self):
        with open(self.entity_dat, 'r') as f:
            for line in [l.strip().split(';') for l in f]:
                self.entity_dict[line[ENTITY_LOC_ID]] = Entity(line[ENTITY_LOC_ID],
                line[ENTITY_NAME], line[ENTITY_DEP_ID], line[ENTITY_FILE])

    def parse_attribute_dat(self):
        with open(self.attribute_dat, 'r') as f:
            for line in [l.strip().split(';') for l in f]:
                attribute = self.attribute_dict.setdefault(line[ATTRIBUTE_LOC_ID],
                    Attribute(line[ATTRIBUTE_LOC_ID], [], []))
                attribute.attribute.append(line[ATTRIBUTE_ATTRIBUTE])
                attribute.value.append(line[ATTRIBUTE_VALUE])
