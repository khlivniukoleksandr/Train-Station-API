import django_filters

from station.models import Train, Route, Journey


class TrainFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name='id', label="Train ID")
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label="Train Name")
    train_type = django_filters.NumberFilter(field_name='train_type', label="Train Type ID")
    train_type_name = django_filters.CharFilter(field_name='train_type__name',
                                                lookup_expr="icontains",
                                                label="Train Type Name")

    class Meta:
        model = Train
        fields = ['id', 'name', 'train_type', 'train_type_name']


class RouteFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name='id', label="Route ID")
    source = django_filters.CharFilter(field_name='source__name', lookup_expr="icontains", label="Route Source Name")
    destination = django_filters.CharFilter(field_name='destination__name', lookup_expr="icontains", label="Route Destination Name")

    class Meta:
        model = Route
        fields = ['id', 'source', 'destination']


class JourneyFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name='id', label="Journey ID")
    route = django_filters.CharFilter(field_name='route__name', lookup_expr="icontains", label="Route Name")
    train = django_filters.CharFilter(field_name='train__name', lookup_expr="icontains", label="Train Name")

    class Meta:
        model = Journey
        fields = ['id', 'route', 'train']
