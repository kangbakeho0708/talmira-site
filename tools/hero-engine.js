/* 탈미라 하늘 엔진: 멈춘 세계라 장면은 한 번만 그린다 */
var TalEngine = (function () {
const FS = `#version 300 es
precision highp float;
out vec4 O;
uniform vec2 R;
uniform vec3 SD, CT, CH, CS, G1, G2;
uniform float TY, FOG, CLD, STR, EXP, SEED, CAMY, PIT, SSZ, SI, MIST, MTN, FGR, MZ, MODE, FLD, PLZ;
uniform int ST, SH;
float h21(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}
float vn(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f);
 return mix(mix(h21(i),h21(i+vec2(1,0)),u.x),mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),u.x),u.y);}
const mat2 M=mat2(1.6,1.2,-1.2,1.6);
float fbm(vec2 p,int o){float a=.5,s=0.;for(int i=0;i<o;i++){s+=a*vn(p);p=M*p;a*=.5;}return s;}
vec3 vnd(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f),du=6.*f*(1.-f);
 float a=h21(i),b=h21(i+vec2(1,0)),c=h21(i+vec2(0,1)),d=h21(i+vec2(1,1));
 return vec3(a+(b-a)*u.x+(c-a)*u.y+(a-b-c+d)*u.x*u.y,du*(vec2(b-a,c-a)+(a-b-c+d)*u.yx));}
float ero(vec2 p,int o){float a=0.,b=1.;vec2 d=vec2(0);for(int i=0;i<o;i++){vec3 n=vnd(p);d+=n.yz;a+=b*n.x/(1.+dot(d,d));b*=.5;p=M*p;}return a;}
float rid(vec2 p,int o){float a=.5,s=0.;for(int i=0;i<o;i++){float n=1.-abs(2.*vn(p)-1.);s+=a*n*n;p=M*p;a*=.5;}return s;}
float heroH(vec2 q,int o){
 float x=q.x,z=q.y; vec2 p=q+SEED*37.;
 float h=-26.+fbm(p*.012,min(o,5))*9.;
 h+=rid(p*vec2(.011,.019),min(o,6))*24.*smoothstep(60.,130.,z)*smoothstep(340.,210.,z);
 float ang=x/max(z,1.);
 float sad=1.-.72*exp(-pow((ang-.36)*3.4,2.));
 float big=(.55+.75*exp(-pow((ang-.36)*1.6,2.)))*(1.-.35*smoothstep(-.2,-.7,ang));
 float e=ero(p*.0042,o);
 h+=pow(max(e,0.),1.7)*150.*smoothstep(250.,430.,z)*sad*big;
 h+=(rid(p*.003+9.,5)*70.-10.)*smoothstep(470.,560.,z);
 float fz=smoothstep(80.,6.,z), fx=max(smoothstep(10.,-30.,x+z*.3),.7*smoothstep(-4.,26.,x-z*.5));
 h+=fz*fx*(62.+rid(p*.05,min(o,7))*14.+fbm(p*.4,3)*1.5*smoothstep(30.,5.,z));
 return h;
}
float Hb(vec2 q,int o){
 float z=q.y; vec2 p=q+SEED*37.;
 if(TY<.5){ return fbm(p*.011,o)*24.-15.+rid(p*.005,4)*34.*smoothstep(200.,480.,z); }
 if(TY<1.5){ vec2 w=p+vec2(fbm(p*.006,3)*90.,fbm(p*.007,2)*30.); float r=1.-abs(2.*vn(w*vec2(.014,.026))-1.); float r2=1.-abs(2.*vn(w*vec2(.05,.09)+3.)-1.); return r*r*14.+r2*r2*1.6+fbm(p*.004,3)*10.-16.; }
 if(TY<2.5){ float m=smoothstep(140.,360.,z); return (rid(p*.011,o)*70.-26.)*m-8.*(1.-m); }
 if(TY<3.5){ float b=fbm(p*.01,min(o,5))*26.-16.; float tr=fbm(p*.07,3)*3.5; return b+tr+rid(p*.005,4)*44.*smoothstep(160.,460.,z); }
 if(TY<4.5){ vec2 w=p+vec2(fbm(p*.01,2)*40.,0.); float dr=1.-abs(2.*vn(w*vec2(.03,.07))-1.); return fbm(p*.01,min(o,4))*8.-8.+dr*dr*1.8+rid(p*.005,o)*95.*smoothstep(90.,380.,z); }
 if(TY<5.5){ float m=smoothstep(.47,.56,fbm(p*.006,5)); return fbm(p*.01,min(o,5))*6.-8.+m*(40.+fbm(p*.04,3)*8.)*smoothstep(30.,150.,z); }
 if(TY<6.5){ return fbm(p*.012,min(o,4))*5.-5.+rid(p*.006,o)*34.*smoothstep(140.,420.,z); }
 return (rid(p*.006,o)*120.-34.)*smoothstep(40.,240.,z)+fbm(p*.02,4)*5.-10.;
}
float H(vec2 q,int o){
 if(TY>7.5) return heroH(q,o);
 float h=Hb(q,o); float x=q.x,z=q.y; vec2 p=q+SEED*37.;
 if(MTN>0.){ float e=ero(p*.0042+11.,o); float ang=x/max(z,1.); float sh=1.-.55*exp(-pow((ang-.3)*2.6,2.)); h+=pow(max(e,0.),1.7)*MTN*smoothstep(MZ,MZ*1.7,z)*sh; h+=(rid(p*.003+9.,5)*MTN*.5-8.)*smoothstep(MZ*1.9,MZ*2.3,z); }
 if(PLZ>0.){ float m=smoothstep(60.,30.,abs(x-z*.0))*smoothstep(PLZ*1.25,PLZ*.9,z)*step(0.,z); h=mix(h,-4.+fbm(p*.01,2)*.4,m); }
 if(FGR>0.){ float fz=smoothstep(80.,6.,z), fx=smoothstep(10.,-30.,x+z*.3); h+=fz*fx*FGR*(1.+rid(p*.05,min(o,7))*.25+fbm(p*.4,3)*.03*smoothstep(30.,5.,z)); }
 return h;
}
const float FAR=700.;
float march(vec3 ro,vec3 rd,out vec3 p){
 float t=.5;
 float lt=t;
 for(int i=0;i<ST;i++){ p=ro+rd*t; int oc=TY>7.5?int(clamp(13.-log2(t+1.),5.,10.)):int(clamp(9.-log2(t+1.),3.,8.)); float d=p.y-H(p.xz,oc); if(d<.002*t){ float a=lt,b=t; for(int k=0;k<6;k++){float m=.5*(a+b); vec3 q=ro+rd*m; if(q.y-H(q.xz,oc)<0.)b=m; else a=m;} t=b; p=ro+rd*t; return t; } if(t>FAR)break; lt=t; t+=max(.2*d,.004*t); }
 if(rd.y<0.&&t<FAR*1.5){ p=ro+rd*t; p.y=H(p.xz,4); return t; }
 return -1.;
}
vec3 nrm(vec3 p,float t){ float e=.004*t+.04; int oc=TY>7.5?int(clamp(13.-log2(t+1.),5.,10.)):int(clamp(9.-log2(t+1.),3.,8.));
 return normalize(vec3(H(p.xz-vec2(e,0),oc)-H(p.xz+vec2(e,0),oc),2.*e,H(p.xz-vec2(0,e),oc)-H(p.xz+vec2(0,e),oc))); }
float shadow(vec3 p){ if(SD.y<.0)return 0.; float r=1.,t=.6; for(int i=0;i<SH;i++){ vec3 q=p+SD*t; float d=q.y-H(q.xz,5); r=min(r,9.*d/t); if(r<.002||q.y>120.)break; t+=clamp(d*.6,.4,25.);} return clamp(r,0.,1.); }
vec3 sky(vec3 rd,bool sun){
 float y=rd.y, mu=dot(rd,SD);
 vec3 c=mix(CH,CT,1.-exp(-max(y,0.)*(TY>7.5?11.:5.5)));
 c=mix(c,CH*.5,smoothstep(0.,-.25,y));
 vec2 a=normalize(rd.xz+1e-4), b=normalize(SD.xz+1e-4);
 float lowSun=smoothstep(.5,-.08,SD.y)*smoothstep(-.45,-.02,SD.y+.1);
 float gi=min(SI,2.);
 c+=CS*gi*.16*exp(-max(y,0.)*9.)*pow(dot(a,b)*.5+.5,5.)*lowSun;
 c+=CS*gi*(.05*pow(max(mu,0.),6.)+.25*pow(max(mu,0.),80.))+CS*SI*.6*pow(max(mu,0.),1200.);
 if(sun) c+=CS*SI*8.*smoothstep(cos(SSZ*1.12),cos(SSZ),mu);
 if(STR>0.){
  vec2 sp=vec2(atan(rd.z,rd.x),asin(clamp(rd.y,-1.,1.)))*150.;
  vec2 id=floor(sp), f=fract(sp)-.5; float hh=h21(id+SEED);
  vec2 off=(vec2(h21(id+3.1),h21(id+7.7))-.5)*.6;
  float s=step(.978,hh)*smoothstep(.16,.0,length(f-off))*(hh-.978)*60.;
  vec3 sc=mix(vec3(.65,.78,1.),vec3(1.,.86,.7),h21(id+1.7));
  float vis=STR*smoothstep(.03,.4,y)*(1.-clamp(dot(c,vec3(.6))*1.5,0.,.95));
  vec3 ax=normalize(vec3(.8,.5,-.15)); float d=dot(rd,ax);
  float mw=exp(-d*d*30.)*(.5+.5*fbm(sp*.02,5));
  float dust=smoothstep(.6,.8,fbm(sp*.03+7.,4))*exp(-d*d*120.);
  c+=(sc*s+vec3(.5,.56,.78)*mw*.07*(1.-dust*.6))*vis;
 }
 return c;
}
vec3 clouds(vec3 ro,vec3 rd,vec3 c){
 if(CLD<=0.||rd.y<=.005) return c;
 float tc=(160.-ro.y)/rd.y; vec2 pc=ro.xz+rd.xz*tc;
 float n=fbm(pc*.0032+SEED*5.,8); n+=.15*fbm(pc*.02,4);
 float d=smoothstep(.52,.9,n)*CLD;
 float mu=max(dot(rd,SD),0.);
 float lit=clamp(SD.y*3.+.6,0.,1.); float gi=min(SI,1.6);
 vec3 col=mix(CH*.5+CT*.5, CS*gi, (.3+.7*pow(mu,3.))*lit);
 col+=CS*gi*smoothstep(.75,.52,n)*pow(mu,6.)*1.2*lit;
 col*=mix(.55,1.,smoothstep(.9,.55,n));
 return mix(c,col,d*exp(-tc*.0006));
}
vec3 fogc(vec3 col,float t,vec3 rd,float py){
 float f=1.-exp(-t*FOG*exp(-max(py,0.)*(TY>2.5&&TY<3.5?.05:.012)));
 f=max(f,smoothstep(FAR*.55,FAR*1.2,t));
 float mu=max(dot(rd,SD),0.);
 vec3 fc=mix(CH*.9,CS*min(SI,1.5)*.7,pow(mu,6.)*.6);
 if(TY>7.5){ vec2 a=normalize(rd.xz+1e-4),b=normalize(SD.xz+1e-4); float side=pow(dot(a,b)*.5+.5,3.); fc=mix(CT*1.8+CH*.12,CH*.9,side*side)+CS*min(SI,2.)*.6*pow(mu,12.); }
 return mix(col,fc,f);
}
vec3 shade(vec3 p,vec3 n,vec3 rd,float t){
 float v=fbm(p.xz*.05,4), v2=fbm(p.xz*.4,2)*smoothstep(80.,10.,t);
 vec3 al=mix(G2,G1,smoothstep(.28,.72,v)*.8+v2*.2);
 al=mix(al,G2*.62,smoothstep(.82,.55,n.y));
 if(TY>3.5&&TY<4.5) al=mix(G2,G1,smoothstep(.5,.8,n.y));
 if(TY>2.5&&TY<3.5) al*=.6+.4*fbm(p.xz*.5,3);
 if(TY>6.5&&TY<7.5) al=mix(al,vec3(.82,.8,.86),smoothstep(30.,46.,p.y)*smoothstep(.55,.8,n.y));
 if(MTN>0.&&TY<7.5&&(TY<.5||TY>3.5)){ float sn=smoothstep(40.,80.,p.y+fbm(p.xz*.05,4)*14.)*smoothstep(.45,.8,n.y); al=mix(al,vec3(.86,.86,.92),sn*step(3.5,TY)); }
 if(TY>7.5){ al*=.75+.5*fbm(vec2(p.y*.35,p.x*.02),3); float sn=smoothstep(18.,52.,p.y+fbm(p.xz*.05,4)*14.)*smoothstep(.42,.78,n.y); al=mix(al,vec3(.86,.84,.9),sn); }
 if(PLZ>0.){ float m=smoothstep(60.,30.,abs(p.x))*smoothstep(PLZ*1.25,PLZ*.9,p.z); vec2 tf=fract(p.xz*.25); float ln=1.-smoothstep(.0,.05,min(min(tf.x,tf.y),min(1.-tf.x,1.-tf.y)))*.0; float grid=smoothstep(.03,.0,min(min(tf.x,1.-tf.x),min(tf.y,1.-tf.y))); vec3 stone=mix(vec3(.58,.55,.48),vec3(.42,.39,.33),grid*.6)*(.92+.08*fbm(p.xz*.3,3)); al=mix(al,stone,m*smoothstep(.8,.95,n.y)); }
 if(FLD>0.){ vec2 fp=p.xz*vec2(.045,.06); fp=mat2(.94,.34,-.34,.94)*fp; vec2 ci=floor(fp), cf=fract(fp); float hc=h21(ci+SEED); vec3 fc=mix(G2*1.1,vec3(.78,.66,.32),smoothstep(.55,.85,hc)); fc=mix(fc,G1*1.15,step(hc,.35)); float edge=smoothstep(.0,.035,min(min(cf.x,cf.y),min(1.-cf.x,1.-cf.y))); float fl8=smoothstep(.86,.97,n.y)*smoothstep(70.,150.,t)*smoothstep(560.,260.,t); al=mix(al,mix(G2*.55,fc,edge),FLD*fl8*step(.2,hc)); }
 float sh=mix(.12,1.,shadow(p+n*.35));
 float dif=max(dot(n,SD),0.)*sh;
 float amb=.55+.45*n.y;
 vec3 bd=normalize(vec3(-SD.x,0.,-SD.z));
 float bk=clamp(dot(n,bd),0.,1.);
 float occ=clamp(.4+.6*smoothstep(-2.,6.,p.y-H(p.xz,3)+2.),0.,1.);
 vec3 skyA=mix(CH,CT,clamp(.3+.55*n.y,0.,1.));
 float night=smoothstep(.02,-.15,SD.y);
 if(TY>7.5){ amb*=.4; dif*=mix(.12,1.,smoothstep(25.,110.,t)); }
 vec3 col=al*(CS*SI*dif*.9+skyA*amb*.75*occ+CH*bk*.15+CS*SI*night*.35*amb);
 float rim=pow(1.-max(dot(n,-rd),0.),6.)*pow(max(dot(rd,SD),0.),4.)*smoothstep(.95,.55,n.y);
 col+=CS*min(SI,2.)*rim*.8*smoothstep(.45,-.05,SD.y)*smoothstep(260.,60.,t)*(TY>2.5&&TY<3.5?.35:1.);
 return col;
}
void main(){
 vec2 uv=(gl_FragCoord.xy*2.-R)/R.y;
 bool sea=TY>1.5&&TY<2.5;
 float base=H(vec2(0.,6.),6);
 vec3 ro=vec3(0.,(sea?0.:(TY>7.5?0.:base))+CAMY,0.);
 vec3 rd=normalize(vec3(uv.x,uv.y+PIT,1.7));
 vec3 p; float t=march(ro,rd,p);
 vec3 col;
 float tw=(sea&&rd.y<0.)?-ro.y/rd.y:1e9;
 if(MODE>.5){ float dd=(sea&&tw<FAR&&(t<0.||tw<t))?tw:(t<0.?FAR*2.:t); float v=clamp(dd/(FAR*2.),0.,1.); float r=floor(v*255.)/255.; float g=floor(fract(v*255.)*255.)/255.; float b=fract(v*65025.); O=vec4(r,g,b,1.); return; }
 if(sea&&tw<FAR&&(t<0.||tw<t)){
  vec3 q=ro+rd*tw; vec2 w=q.xz*.3; float e=.06;
  float w0=fbm(w,5), wx=fbm(w+vec2(e,0),5), wz=fbm(w+vec2(0,e),5);
  vec3 n=normalize(vec3((w0-wx)*.9,1.,(w0-wz)*.9)); n=normalize(mix(n,vec3(0,1,0),smoothstep(20.,400.,tw)));
  vec3 rr=reflect(rd,n); rr.y=abs(rr.y);
  float fr=.03+.97*pow(1.-max(dot(-rd,n),0.),5.);
  vec3 rc=clouds(q,rr,sky(rr,false));
  rc+=CS*SI*(4.*pow(max(dot(rr,SD),0.),1500.)+.35*pow(max(dot(rr,SD),0.),120.));
  col=mix(G2*.3*(CT+CH),rc,fr);
  col=fogc(col,tw,rd,0.);
 } else if(t<0.){
  col=clouds(ro,rd,sky(rd,true));
  if(TY>7.5&&rd.y>.002){
   float tc=(300.-ro.y)/rd.y; vec2 pc=ro.xz+rd.xz*tc;
   float n=fbm(pc*vec2(.0009,.006)+SEED*3.,7)+.12*fbm(pc*.01,4);
   float d=smoothstep(.56,.88,n)*.75*smoothstep(.0,.03,rd.y)*smoothstep(.3,.06,rd.y);
   float mu=max(dot(rd,SD),0.);
   vec3 cc=mix(CT*.9+CH*.06,CS*SI*.6,clamp(pow(mu,4.)*.95+smoothstep(.1,.0,rd.y)*.25,0.,1.));
   cc+=CS*SI*.5*pow(mu,14.)*smoothstep(.8,.55,n);
   col=mix(col,cc,d);
  }
 } else {
  vec3 n=nrm(p,t);
  col=shade(p,n,rd,t);
  col=fogc(col,t,rd,p.y);
 }
 if(MIST>0.&&rd.y<0.){
  float top=TY>7.5?-3.:Hb(vec2(0.,40.),4)+6.;
  float t0=max((top-ro.y)/rd.y,0.), t1=t<0.?FAR:min(t,FAR);
  if(t1>t0){
   float mu=max(dot(rd,SD),0.);
   vec3 lc=mix(CH*.16+CT*.7,CS*SI*.4,pow(mu,6.)*.9)+CS*SI*.6*pow(mu,40.);
   float tr=1.; vec3 acc=vec3(0.); float dt=(t1-t0)/24.;
   for(int i=0;i<24;i++){
    float tt=t0+dt*(float(i)+h21(gl_FragCoord.xy+float(i)));
    vec3 q=ro+rd*tt;
    float dn=smoothstep(top,top-9.,q.y)*smoothstep(.4,.78,fbm(q.xz*vec2(.006,.013)+SEED,5))*.035;
    float hl=.55+.45*smoothstep(top-12.,top,q.y);
    dn*=MIST; acc+=tr*dn*dt*lc*hl; tr*=exp(-dn*dt);
    if(tr<.02)break;
   }
   col=col*tr+acc;
  }
 }
 col*=EXP;
 col=(col*(2.51*col+.03))/(col*(2.43*col+.59)+.14);
 col=pow(clamp(col,0.,1.),vec3(1./2.2));
 col+=(h21(gl_FragCoord.xy+SEED*91.)-.5)*.022;
 vec2 qv=gl_FragCoord.xy/R; col*=.78+.22*pow(16.*qv.x*qv.y*(1.-qv.x)*(1.-qv.y),.18);
 O=vec4(col,1.);
}`;
const VS = `#version 300 es
in vec2 a; void main(){gl_Position=vec4(a,0.,1.);}`;

const lin = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => Math.pow(v / 255, 2.2)); };
const sunDir = (el, az) => { const e = el * Math.PI / 180, a = az * Math.PI / 180; return [Math.sin(a) * Math.cos(e), Math.sin(e), Math.cos(a) * Math.cos(e)]; };
const DEF = { mode: 0, fld: 0, plz: 0, mist: 0, mtn: 0, fgr: 0, mz: 250, ty: 0, el: 5, az: 0, top: '#20304f', hor: '#e9c8a0', sun: '#ffd9a0', si: 3, g1: '#5d7a3a', g2: '#3a4d2a', fog: .005, cld: .4, str: 0, exp: 1, seed: 1, camy: 3, pit: .24, ssz: .03 };
const QUAL = { bake: { s: 1, st: 420, sh: 72, cap: 9e6, band: 12e4 }, low: { s: .6, st: 100, sh: 16, cap: 7e5, band: 4e4 }, mid: { s: 1, st: 170, sh: 32, cap: 2.2e6, band: 6e4 }, high: { s: 1.6, st: 280, sh: 56, cap: 7e6, band: 9e4 } };

let gl = null, cv = null, prog = null, U = {}, lost = false, ready = null;
const fail = (why) => { console.warn('엔진 대체 그림 사용:', why); prog = null; gl = false; };
const init = () => !!(gl && prog && !lost);
const prepare = () => {
  if (ready) return ready;
  ready = new Promise((res) => {
    try {
      cv = document.createElement('canvas');
      gl = cv.getContext('webgl2', { preserveDrawingBuffer: true, antialias: false, powerPreference: 'high-performance' }) || false;
      if (!gl) { fail('webgl2 없음'); res(false); return; }
      cv.addEventListener('webglcontextlost', (e) => { e.preventDefault(); lost = true; fail('맥락 잃음'); });
      const ext = gl.getExtension('KHR_parallel_shader_compile');
      const sh = (t, src) => { const o = gl.createShader(t); gl.shaderSource(o, src); gl.compileShader(o); return o; };
      const vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
      prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
      const t0 = performance.now();
      const finish = () => {
        if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { fail(gl.getShaderInfoLog(fs) || gl.getProgramInfoLog(prog)); res(false); return; }
        gl.useProgram(prog);
        const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
        const loc = gl.getAttribLocation(prog, 'a'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
        ['R', 'SD', 'CT', 'CH', 'CS', 'G1', 'G2', 'TY', 'FOG', 'CLD', 'STR', 'EXP', 'SEED', 'CAMY', 'PIT', 'SSZ', 'SI', 'MIST', 'MTN', 'FGR', 'MZ', 'MODE', 'FLD', 'PLZ', 'ST', 'SH'].forEach((k) => { U[k] = gl.getUniformLocation(prog, k); });
        res(true);
      };
      if (!ext) { setTimeout(finish, 0); return; }
      const poll = () => {
        if (gl.getProgramParameter(prog, ext.COMPLETION_STATUS_KHR)) { finish(); return; }
        if (performance.now() - t0 > 12000) { fail('셰이더 준비 시간 초과'); res(false); return; }
        setTimeout(poll, 50);
      };
      poll();
    } catch (e) { fail(e); res(false); }
  });
  return ready;
};
/* 그래픽 칩 이름으로 기본 화질 고르기 */
const gpuName = () => {
  try { const c = document.createElement('canvas').getContext('webgl2'); if (!c) return ''; const x = c.getExtension('WEBGL_debug_renderer_info'); const n = x ? c.getParameter(x.UNMASKED_RENDERER_WEBGL) : c.getParameter(c.RENDERER); const l = c.getExtension('WEBGL_lose_context'); if (l) l.loseContext(); return String(n || ''); } catch (e) { return ''; }
};
/* 그리기: 띠로 잘라 한 프레임에 한 띠씩. 멈춘 세계라 한 번 그리면 끝 */
const fallback = (ctx, w, h, P) => {
  const g = ctx.createLinearGradient(0, 0, 0, h); g.addColorStop(0, P.top); g.addColorStop(.6, P.hor); g.addColorStop(.62, P.g2); g.addColorStop(1, '#050507');
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
};
const setU = (P, q, rw, rh, st, sh) => {
  gl.uniform2f(U.R, rw, rh); gl.uniform3fv(U.SD, sunDir(P.el, P.az));
  gl.uniform3fv(U.CT, lin(P.top)); gl.uniform3fv(U.CH, lin(P.hor)); gl.uniform3fv(U.CS, lin(P.sun));
  gl.uniform3fv(U.G1, lin(P.g1)); gl.uniform3fv(U.G2, lin(P.g2));
  gl.uniform1f(U.TY, P.ty); gl.uniform1f(U.FOG, P.fog); gl.uniform1f(U.CLD, P.cld); gl.uniform1f(U.STR, P.str);
  gl.uniform1f(U.EXP, P.exp); gl.uniform1f(U.SEED, P.seed); gl.uniform1f(U.CAMY, P.camy); gl.uniform1f(U.PIT, P.pit); gl.uniform1f(U.SSZ, P.ssz); gl.uniform1f(U.SI, P.si); gl.uniform1f(U.MIST, P.mist || 0); gl.uniform1f(U.MTN, P.mtn || 0); gl.uniform1f(U.FGR, P.fgr || 0); gl.uniform1f(U.MZ, P.mz || 250); gl.uniform1f(U.MODE, P.mode || 0); gl.uniform1f(U.FLD, P.fld || 0); gl.uniform1f(U.PLZ, P.plz || 0);
  gl.uniform1i(U.ST, st); gl.uniform1i(U.SH, sh);
};
const frame = () => new Promise((r) => requestAnimationFrame(() => r()));
const Q = []; let busy = false;
const pump = () => {
  if (busy || !Q.length) return;
  busy = true; const j = Q.shift();
  run(j).then(() => true, (e) => { console.warn(e); return false; }).then((ok) => { busy = false; j.done(ok); pump(); });
};
const run = async (j) => {
  const P = Object.assign({}, DEF, j.params), q = QUAL[j.quality] || QUAL.mid;
  const ctx = j.target.getContext('2d'), w = j.target.width, h = j.target.height;
  await prepare();
  if (!init()) { const t2 = j.into || j.target; fallback(t2.getContext('2d'), t2.width, t2.height, P); if (j.onPreview) j.onPreview(); return; }
  if (j.preview) {
    const pw = Math.max(2, Math.round(w * .18)), ph = Math.max(2, Math.round(h * .18));
    cv.width = pw; cv.height = ph; gl.viewport(0, 0, pw, ph); setU(P, q, pw, ph, 70, 0);
    gl.drawArrays(gl.TRIANGLES, 0, 3); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(cv, 0, 0, w, h);
    if (j.onPreview) j.onPreview();
    await frame();
  }
  let k = q.s; if (w * h * k * k > q.cap) k = Math.sqrt(q.cap / (w * h));
  const rw = Math.max(2, Math.round(w * k)), rh = Math.max(2, Math.round(h * k));
  cv.width = rw; cv.height = rh; gl.viewport(0, 0, rw, rh); setU(P, q, rw, rh, P.ty > 7.5 ? Math.max(q.st * 2, 240) : q.st, q.sh);
  const bh = Math.max(2, Math.floor(q.band / rw));
  gl.enable(gl.SCISSOR_TEST);
  for (let y = 0; y < rh; y += bh) { if (lost) return; gl.scissor(0, y, rw, bh); gl.drawArrays(gl.TRIANGLES, 0, 3); gl.flush(); await frame(); }
  gl.disable(gl.SCISSOR_TEST);
  if (j.into) { const c2 = j.into.getContext('2d'); c2.imageSmoothingQuality = 'high'; c2.drawImage(cv, 0, 0, j.into.width, j.into.height); }
  else { ctx.imageSmoothingQuality = 'high'; ctx.drawImage(cv, 0, 0, w, h); }
};
/* target: 2D 캔버스. opts: preview(빠른 미리보기), into(다 그린 뒤 넣을 다른 캔버스), prio */
const render = (target, params, quality, opts) => new Promise((done) => {
  const o = opts || {};
  Q.push(Object.assign({ target, params, quality, done }, o));
  Q.sort((a, b) => (b.prio || 0) - (a.prio || 0));
  pump();
});
const clear = () => { Q.splice(0).forEach((j) => j.done(false)); };
/* 해가 화면 어디에 있나 (0..1, 위가 0) */
const sunScreen = (params, w, h) => {
  const P = Object.assign({}, DEF, params), d = sunDir(P.el, P.az);
  if (d[2] <= 0) return null;
  const ux = 1.7 * d[0] / d[2], uy = 1.7 * d[1] / d[2] - P.pit;
  return { x: (ux * h + w) / 2 / w, y: 1 - (uy * h + h) / 2 / h };
};
return { render, clear, sunScreen, gpuName, ok: () => init() };
})();
