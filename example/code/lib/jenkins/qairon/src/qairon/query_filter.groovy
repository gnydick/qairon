package qairon

class QueryFilter {
    // have to return something like
    // [{"name":"service_id","op":"in","val":' + svc_ids + '}]

    private GString filter

    QueryFilter(String field, String op, String value) {
        this.filter = "[{\"name\":\"${field}\",\"op\":\"${op}\",\"val\":\"${value}\"}]"
    }

    public GString getFilter() {
        return this.filter
    }

}